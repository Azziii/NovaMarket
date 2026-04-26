| Этап | Тип события | Название |
|------|------------|---------|
| Заказ создан | domain | OrderCreated |
| Запрос резерва товаров | command | ReserveItemsRequested |
| Резерв успешен | domain | ItemsReserved |
| Резерв не удался | failure | ItemsReservationFailed |
| Запрос оплаты | command | PaymentRequested |
| Оплата успешна | domain | PaymentSucceeded |
| Оплата неуспешна | failure | PaymentFailed |
| Отмена заказа | compensation | OrderCancelled |
| Отмена резерва | compensation | ItemsReservationCancelled |
| Возврат средств | compensation | PaymentRefunded |
| Создание доставки | domain | DeliveryCreated |
| Заказ завершён | domain | OrderCompleted |