# **Название задачи:**

Реализация просмотра истории заказов (NovaMarket)

---

## **Автор:**
Митрофанов Роман

---

## **Дата:**
2026-04-20

---

# **Функциональные требования**

| № | Действующие лица или системы | Use Case | Описание |
|---|------------------------------|----------|----------|
| 1 | Покупатель | Просмотр списка заказов | 1. Пользователь открывает личный кабинет<br>2. Система запрашивает список заказов<br>3. Отображаются дата, сумма, статус, способ доставки |
| 2 | Покупатель | Просмотр деталей заказа | 1. Пользователь выбирает заказ<br>2. Система отображает состав заказа<br>3. Показываются товары, цены, количество, доставка, оплата |
| 3 | Покупатель | Просмотр статуса | Отображение статуса (доставлен, отменён, в пути) |
| 4 | Покупатель | Скачивание чека | 1. Пользователь запрашивает чек<br>2. Система возвращает данные об оплате |
| 5 | Покупатель | Повторный заказ | 1. Пользователь нажимает «повторить заказ»<br>2. Товары добавляются в корзину |
| 6 | Система | Агрегация данных | Сбор данных из Order, Payment, Delivery сервисов |
| 7 | Система | Обновление read-модели | Обновление агрегированных данных при поступлении событий |

---

# **Нефункциональные требования**

| № | Требование |
|---|------------|
| 1 | Время отклика ≤ 300 мс для 98% запросов |
| 2 | SLA ≤ 1 сек для 99.99% |
| 3 | Масштабируемость до 40 000+ заказов в день |
| 4 | Горизонтальное масштабирование |
| 5 | Слабая связность сервисов |
| 6 | Высокая доступность |
| 7 | Event-driven архитектура |
| 8 | Устойчивость к сбоям (retry, DLQ) |
| 9 | Расширяемость (подключение новых сервисов) |

---

# **Решение**

В рамках проектирования рассмотрены два архитектурных подхода.

---

## **Вариант 1 - API Composition**

### **Описание**

Агрегация данных происходит в момент запроса:
- API Gateway или BFF вызывает несколько сервисов
- агрегирует ответы
- возвращает клиенту

### **Контейнерная диаграмма (C2)**

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(customer, "Customer")

System_Boundary(system, "NovaMarket") {
    Container(api, "API Gateway", "NGINX", "Точка входа")
    Container(order, "Order Service", "Service", "Заказы")
    Container(payment, "Payment Service", "Service", "Оплата")
    Container(delivery, "Delivery Service", "Service", "Доставка")
}

Rel(customer, api, "HTTP")
Rel(api, order, "REST")
Rel(api, payment, "REST")
Rel(api, delivery, "REST")
@enduml
```

### **Плюсы**
- простая реализация
- нет дублирования данных

### **Минусы**
- высокая задержка
- риск таймаутов
- сильная связность
- не проходит SLA

---

## **Вариант 2 - CQRS + Read Model (выбранный)**

### **Описание**

Используется разделение:
- write-модель (основные сервисы)
- read-модель (отдельный сервис)

### **Контейнерная диаграмма (C2)**

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(customer, "Customer")

System_Boundary(system, "NovaMarket") {

    Container(api, "API Gateway", "NGINX", "Входная точка")

    Container(order, "Order Service", "Kotlin", "Создание заказов (write)")
    Container(inventory, "Inventory Service", "Kotlin", "Резервы")
    Container(payment, "Payment Service", "Kotlin", "Оплата")
    Container(delivery, "Delivery Service", "Kotlin", "Доставка")

    Container(kafka, "Kafka", "Event Broker", "События")

    Container(query, "Order Query Service", "Kotlin", "Чтение истории заказов")
    ContainerDb(read_db, "Read DB", "PostgreSQL / NoSQL", "Денормализованная модель")
}

Rel(customer, api, "HTTP")

Rel(api, order, "REST (write)")
Rel(api, query, "REST (read)")

Rel(order, kafka, "publishes")
Rel(inventory, kafka, "publishes")
Rel(payment, kafka, "publishes")
Rel(delivery, kafka, "publishes")

Rel(kafka, query, "consumes events")

Rel(query, read_db, "reads/writes")

@enduml
```

---

## **Поток данных**

1. Order Service публикует OrderCreated  
2. Payment Service публикует PaymentSucceeded  
3. Delivery Service публикует DeliveryCreated  
4. Query Service обновляет read-модель  
5. Клиент получает агрегированные данные  

---

## **Сравнение решений**

| Критерий | API Composition | CQRS |
|----------|----------------|------|
| Скорость | Низкая | Высокая |
| Масштабируемость | Низкая | Высокая |
| Связность | Высокая | Низкая |
| Сложность | Низкая | Средняя |
| Соответствие EDA | Нет | Да |

---

## **Итоговое решение**

Выбран CQRS + Read Model

---

## **Обоснование выбора**

- Требование по latency ≤ 300 мс
- Высокая нагрузка
- Необходимость агрегированных данных
- Соответствие EDA архитектуре
- Возможность масштабирования чтения

---

# **Альтернативы**

### API Composition
Отклонён из-за:
- высокой задержки
- зависимости от сервисов
- проблем масштабирования

### Event Sourcing
Не выбран:
- высокая сложность
- избыточен для MVP

---

# **Недостатки, ограничения, риски**

## **Основные**
- eventual consistency
- дублирование данных
- сложность поддержки read-модели

## **Технические**
- потеря событий - требуется retry/DLQ
- рассинхронизация данных
- необходимость идемпотентности

## **Архитектурные**
- рост сложности системы
- необходимость мониторинга Kafka
- управление схемами событий
