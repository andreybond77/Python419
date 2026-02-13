import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { CartItem } from '../types';

export const CartPage: React.FC = () => {
  const { items, totalItems, totalPrice, removeFromCart, updateQuantity, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [orderData, setOrderData] = useState({
    deliveryAddress: user?.address || '',
    phone: '',
    notes: ''
  });

  const handleQuantityChange = (productId: number, newQuantity: number) => {
    if (newQuantity < 1) {
      handleRemoveItem(productId);
      return;
    }
    if (newQuantity > 99) {
      newQuantity = 99;
    }
    updateQuantity(productId, newQuantity);
  };

  const handleRemoveItem = (productId: number) => {
    if (window.confirm('Удалить товар из корзины?')) {
      removeFromCart(productId);
    }
  };

  const handleClearCart = () => {
    if (items.length === 0) return;
    if (window.confirm('Вы уверены, что хотите очистить всю корзину?')) {
      clearCart();
    }
  };

  const handleCheckout = () => {
    if (!user) {
      alert('Пожалуйста, войдите в аккаунт для оформления заказа');
      navigate('/login');
      return;
    }
    if (items.length === 0) {
      alert('Корзина пуста');
      return;
    }
    if (!orderData.deliveryAddress.trim()) {
      alert('Введите адрес доставки');
      return;
    }
    if (!orderData.phone.trim()) {
      alert('Введите номер телефона');
      return;
    }

    // Вместо перехода на несуществующую страницу /checkout,
    // показываем сообщение об успешном оформлении
    handleOrderSubmit();
  };

  const handleOrderSubmit = async () => {
    try {
      // Имитация отправки заказа
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      alert('Заказ успешно оформлен! С вами свяжется наш магазин.');
      
      // Очищаем корзину после успешного заказа
      clearCart();
      
      // Перенаправляем на страницу заказов
      navigate('/orders');
    } catch (error) {
      alert('Произошла ошибка при оформлении заказа. Попробуйте еще раз.');
    }
  };

  // Показать loading если данные загружаются
  if (!user) {
    return (
      <div className="container py-5">
        <div className="text-center py-5">
          <div className="mb-4">
            <i className="bi bi-shield-lock display-1 text-potion"></i>
          </div>
          <h2 className="mb-4">Доступ к корзине ограничен</h2>
          <p className="lead mb-4">Для доступа к корзине необходимо войти в магический аккаунт</p>
          <div className="d-flex justify-content-center gap-3">
            <Link to="/login" className="btn btn-potion btn-lg">
              <i className="bi bi-key me-2"></i>Войти в аккаунт
            </Link>
            <Link to="/register" className="btn btn-outline-potion btn-lg">
              <i className="bi bi-person-plus me-2"></i>Создать аккаунт
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Если корзина пуста
  if (items.length === 0) {
    return (
      <div className="container py-5">
        <div className="text-center py-5">
          <div className="mb-4">
            <i className="bi bi-basket display-1 text-muted"></i>
          </div>
          <h2 className="mb-4">Ваша корзина пуста</h2>
          <p className="lead mb-4">Добавьте магические зелья из каталога, чтобы сделать заказ</p>
          <Link to="/potions" className="btn btn-potion btn-lg">
            <i className="bi bi-flask me-2"></i>Перейти к каталогу зелий
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="py-5">
      <h1 className="mb-4 text-potion"><i className="bi bi-basket me-3"></i>Корзина покупок</h1>
      
      <div className="row">
        {/* Левая колонка - список товаров */}
        <div className="col-lg-8 mb-4">
          <div className="card potion-card">
            <div className="card-header bg-moonlight border-bottom border-potion">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0 text-white">
                  <i className="bi bi-flask me-2"></i>
                  Зелья в корзине ({totalItems} шт.)
                </h5>
                <button 
                  onClick={handleClearCart} 
                  className="btn btn-sm btn-outline-danger"
                  disabled={items.length === 0}
                >
                  <i className="bi bi-trash me-1"></i> Очистить корзину
                </button>
              </div>
            </div>
            
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-dark table-hover mb-0">
                  <thead className="bg-dark-purple">
                    <tr>
                      <th scope="col" style={{ width: '40%' }}>Зелье</th>
                      <th scope="col" style={{ width: '15%' }}>Цена</th>
                      <th scope="col" style={{ width: '20%' }}>Количество</th>
                      <th scope="col" style={{ width: '15%' }}>Сумма</th>
                      <th scope="col" style={{ width: '10%' }}>Действие</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item: CartItem) => (
                      <tr key={item.productId}>
                        <td className="align-middle">
                          <div className="d-flex align-items-center">
                            <div 
                              className="rounded me-3 d-flex align-items-center justify-content-center"
                              style={{
                                width: '50px',
                                height: '50px',
                                backgroundColor: 'var(--potion-purple)',
                                color: 'white'
                              }}
                            >
                              <i className="bi bi-flask fs-5"></i>
                            </div>
                            <div>
                              <h6 className="mb-0 text-moonlight">{item.name}</h6>
                              <small className="text-muted">
                                {item.category ? `Категория: ${item.category}` : `ID: ${item.productId}`}
                              </small>
                            </div>
                          </div>
                        </td>
                        <td className="align-middle">
                          <strong className="text-success">{item.price.toFixed(2)} гол.</strong>
                        </td>
                        <td className="align-middle">
                          <div className="d-flex align-items-center">
                            <button
                              className="btn btn-sm btn-outline-potion"
                              onClick={() => handleQuantityChange(item.productId, item.quantity - 1)}
                              disabled={item.quantity <= 1}
                              style={{ minWidth: '36px' }}
                            >
                              <i className="bi bi-dash"></i>
                            </button>
                            <input
                              type="number"
                              min="1"
                              max="99"
                              className="form-control form-control-sm text-center mx-2"
                              value={item.quantity}
                              onChange={(e) => {
                                const value = parseInt(e.target.value);
                                if (!isNaN(value)) {
                                  handleQuantityChange(item.productId, value);
                                }
                              }}
                              style={{ 
                                maxWidth: '70px', 
                                color: '#e6e6ff',
                                backgroundColor: '#1a0033',
                                borderColor: 'var(--potion-purple)'
                              }}
                            />
                            <button
                              className="btn btn-sm btn-outline-potion"
                              onClick={() => handleQuantityChange(item.productId, item.quantity + 1)}
                              disabled={item.quantity >= 99}
                              style={{ minWidth: '36px' }}
                            >
                              <i className="bi bi-plus"></i>
                            </button>
                          </div>
                        </td>
                        <td className="align-middle">
                          <strong className="text-success">
                            {(item.price * item.quantity).toFixed(2)} гол.
                          </strong>
                        </td>
                        <td className="align-middle">
                          <button
                            onClick={() => handleRemoveItem(item.productId)}
                            className="btn btn-sm btn-outline-danger"
                            title="Удалить"
                            style={{ width: '36px', height: '36px' }}
                          >
                            <i className="bi bi-trash"></i>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="card-footer bg-dark-purple border-top border-potion">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <strong className="text-moonlight">Всего товаров:</strong> {totalItems} шт.
                </div>
                <div>
                  <strong className="text-moonlight">Общая сумма:</strong>
                  <span className="h4 text-potion ms-2">{totalPrice.toFixed(2)} гол.</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-3 d-flex gap-2">
            <Link to="/potions" className="btn btn-outline-potion">
              <i className="bi bi-arrow-left me-2"></i>
              Продолжить покупки
            </Link>
            <button 
              onClick={handleClearCart}
              className="btn btn-outline-danger"
              disabled={items.length === 0}
            >
              <i className="bi bi-trash me-2"></i>
              Очистить корзину
            </button>
          </div>
        </div>

        {/* Правая колонка - оформление заказа */}
        <div className="col-lg-4">
          <div className="card potion-card mb-4">
            <div className="card-header bg-moonlight border-bottom border-potion">
              <h5 className="mb-0 text-white">
                <i className="bi bi-geo-alt me-2"></i>
                Данные для доставки
              </h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label text-moonlight">
                  <i className="bi bi-geo-alt me-1"></i>
                  Адрес доставки:
                </label>
                <textarea
                  className="form-control bg-dark-purple border-potion text-white"
                  value={orderData.deliveryAddress}
                  onChange={(e) => setOrderData({...orderData, deliveryAddress: e.target.value})}
                  rows={2}
                  placeholder="Введите полный адрес доставки"
                  style={{ color: '#e6e6ff' }}
                  required
                />
              </div>
              
              <div className="mb-3">
                <label className="form-label text-moonlight">
                  <i className="bi bi-telephone me-1"></i>
                  Контактный телефон:
                </label>
                <input
                  type="tel"
                  className="form-control bg-dark-purple border-potion text-white"
                  value={orderData.phone}
                  onChange={(e) => setOrderData({...orderData, phone: e.target.value})}
                  placeholder="+7 (XXX) XXX-XX-XX"
                  style={{ color: '#e6e6ff' }}
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="form-label text-moonlight">
                  <i className="bi bi-chat-left-text me-1"></i>
                  Примечания к заказу:
                </label>
                <textarea
                  className="form-control bg-dark-purple border-potion text-white"
                  value={orderData.notes}
                  onChange={(e) => setOrderData({...orderData, notes: e.target.value})}
                  rows={2}
                  placeholder="Особые пожелания, время доставки и т.д."
                  style={{ color: '#e6e6ff' }}
                />
              </div>
              
              <div className="alert alert-info small">
                <i className="bi bi-info-circle me-2"></i>
                Наш курьер свяжется с вами для подтверждения заказа и уточнения деталей доставки.
              </div>
            </div>
          </div>
          
          <div className="card potion-card sticky-top" style={{ top: '20px' }}>
            <div className="card-header bg-moonlight border-bottom border-potion">
              <h5 className="mb-0 text-white">
                <i className="bi bi-receipt me-2"></i>
                Сумма заказа
              </h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <div className="d-flex justify-content-between mb-2">
                  <span className="text-moonlight">Товары ({totalItems} шт.):</span>
                  <span className="text-success">{totalPrice.toFixed(2)} гол.</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span className="text-moonlight">Доставка:</span>
                  <span className="text-success">0.00 гол.</span>
                </div>
                <hr className="border-potion my-2" />
                <div className="d-flex justify-content-between">
                  <span className="h5 text-moonlight">Итого к оплате:</span>
                  <span className="h4 text-potion">{totalPrice.toFixed(2)} гол.</span>
                </div>
              </div>
              
              <button
                className="btn btn-potion btn-lg w-100"
                onClick={handleCheckout}
                disabled={items.length === 0}
              >
                <i className="bi bi-credit-card me-2"></i>
                Оформить заказ
              </button>
              
              <Link to="/potions" className="btn btn-outline-potion w-100 mt-2">
                <i className="bi bi-arrow-left me-2"></i>
                Продолжить покупки
              </Link>
              
              <div className="mt-3 text-center">
                <small className="text-muted">
                  Нажимая кнопку, вы соглашаетесь с условиями покупки
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;