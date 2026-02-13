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
  const [isCreatingOrder, setIsCreatingOrder] = useState(false);
  const [selectedDelivery, setSelectedDelivery] = useState('portal');

  // Функция для создания fallback изображения
  const getFallbackImage = (name: string, category: string) => {
    const colors: Record<string, string> = {
      'physical': '#ff6b6b',
      'mental': '#4dffea',
      'healing': '#38b000',
      'transformative': '#ff9e00',
      'protective': '#4361ee',
      'combat': '#f72585',
      'poison': '#6a040f',
      'unknown': '#9d4edd'
    };
    
    const color = colors[category] || '#9d4edd';
    const firstLetter = name.charAt(0).toUpperCase();
    
    return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
      <rect width="60" height="60" fill="#1a0033" rx="5"/>
      <rect x="15" y="10" width="30" height="40" rx="3" fill="${color}" opacity="0.8"/>
      <rect x="17" y="7" width="26" height="6" rx="2" fill="${color}" opacity="0.7"/>
      <rect x="20" y="53" width="20" height="4" rx="1" fill="${color}" opacity="0.6"/>
      <circle cx="30" cy="25" r="6" fill="white" opacity="0.4"/>
      <circle cx="35" cy="30" r="5" fill="white" opacity="0.5"/>
      <circle cx="25" cy="35" r="4" fill="white" opacity="0.3"/>
      <text x="30" y="48" text-anchor="middle" fill="white" font-family="Arial" font-size="10" font-weight="bold">${firstLetter}</text>
    </svg>`;
  };

  // Функция для получения русского названия категории
  const getCategoryLabel = (category: string): string => {
    const categories: Record<string, string> = {
      'physical': 'Физическое',
      'mental': 'Психическое',
      'healing': 'Целительное',
      'transformative': 'Преображающее',
      'protective': 'Защитное',
      'combat': 'Боевое',
      'poison': 'Яд',
      'unknown': 'Неизвестно'
    };
    return categories[category] || category;
  };

  const handleQuantityChange = (productId: number, newQuantity: number) => {
    if (newQuantity >= 1 && newQuantity <= 99) {
      updateQuantity(productId, newQuantity);
    }
  };

  const handleRemoveItem = (productId: number) => {
    if (window.confirm('Удалить зелье из корзины?')) {
      removeFromCart(productId);
    }
  };

  const handleClearCart = () => {
    if (window.confirm('Очистить всю корзину?')) {
      clearCart();
    }
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    
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

    setIsCreatingOrder(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      alert('Заказ успешно оформлен! С вами свяжется наш маг-курьер.');
      
      clearCart();
      setOrderData({ deliveryAddress: '', phone: '', notes: '' });
      
      navigate('/orders');
    } catch (error) {
      alert('Ошибка при оформлении заказа. Попробуйте снова.');
    } finally {
      setIsCreatingOrder(false);
    }
  };

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
              <i className="bi bi-key me-2"></i>
              Войти
            </Link>
            <Link to="/register" className="btn btn-outline-potion btn-lg">
              <i className="bi bi-person-plus me-2"></i>
              Зарегистрироваться
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="container py-5">
        <div className="text-center py-5">
          <div className="mb-4">
            <i className="bi bi-basket display-1 text-muted"></i>
          </div>
          <h2 className="mb-3">Ваша корзина пуста</h2>
          <p className="text-muted mb-4 fs-5">Добавьте магические зелья из каталога, чтобы сделать заказ</p>
          <Link to="/potions" className="btn btn-potion btn-lg px-5">
            <i className="bi bi-arrow-right me-2"></i>
            Перейти к зельям
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="py-5">
      <h1 className="mb-4 text-potion">
        <i className="bi bi-basket me-3"></i>
        Корзина покупок
      </h1>
      
      <div className="row">
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
                >
                  <i className="bi bi-trash me-1"></i>
                  Очистить корзину
                </button>
              </div>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-dark table-hover mb-0">
                  <thead className="bg-dark-purple">
                    <tr>
                      <th style={{ width: '50px' }}>№</th>
                      <th>Зелье</th>
                      <th style={{ width: '100px' }}>Цена</th>
                      <th style={{ width: '120px' }}>Количество</th>
                      <th style={{ width: '100px' }}>Сумма</th>
                      <th style={{ width: '50px' }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item: CartItem, index: number) => (
                      <tr key={item.productId}>
                        <td className="align-middle">{index + 1}</td>
                        <td>
                          <div className="d-flex align-items-center">
                            <div style={{
                              position: 'relative',
                              width: '70px',
                              height: '70px',
                              minWidth: '70px',
                              marginRight: '15px'
                            }}>
                              <div style={{
                                width: '100%',
                                height: '100%',
                                borderRadius: '8px',
                                backgroundColor: '#1a0033',
                                border: '2px solid var(--potion-purple)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                overflow: 'hidden'
                              }}>
                                <img 
                                  src={item.image_url || getFallbackImage(item.name, item.category)}
                                  alt={item.name}
                                  style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                    objectPosition: 'center'
                                  }}
                                  onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.onerror = null;
                                    target.src = getFallbackImage(item.name, item.category);
                                  }}
                                />
                              </div>
                              <div style={{
                                position: 'absolute',
                                bottom: '-5px',
                                right: '-5px',
                                backgroundColor: 'var(--potion-purple)',
                                color: 'white',
                                borderRadius: '50%',
                                width: '24px',
                                height: '24px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '12px',
                                fontWeight: 'bold',
                                border: '2px solid #1a0033'
                              }}>
                                {item.quantity}
                              </div>
                            </div>
                            <div style={{ flex: 1 }}>
                              <h6 className="mb-1 text-moonlight">{item.name}</h6>
                              <div className="d-flex align-items-center gap-2">
                                <span className="badge bg-dark border border-potion small">
                                  {getCategoryLabel(item.category)}
                                </span>
                                <small className="text-muted">ID: {item.productId}</small>
                              </div>
                              <div className="mt-1">
                                <small className="text-potion">
                                  <i className="bi bi-coin me-1"></i>
                                  {item.price.toFixed(2)} гол. / шт.
                                </small>
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="align-middle">
                          <strong className="text-success">{item.price.toFixed(2)} гол.</strong>
                        </td>
                        <td className="align-middle">
                          <div className="input-group input-group-sm" style={{ maxWidth: '140px' }}>
                            <button 
                              className="btn btn-outline-potion"
                              type="button"
                              onClick={() => handleQuantityChange(item.productId, item.quantity - 1)}
                              disabled={item.quantity <= 1}
                              style={{ minWidth: '30px' }}
                            >
                              <i className="bi bi-dash"></i>
                            </button>
                            <input 
                              type="number" 
                              className="form-control text-center bg-dark border-potion text-white"
                              value={item.quantity}
                              min="1"
                              max="99"
                              onChange={(e) => handleQuantityChange(item.productId, parseInt(e.target.value) || 1)}
                              style={{ 
                                color: '#e6e6ff',
                                minWidth: '40px'
                              }}
                            />
                            <button 
                              className="btn btn-outline-potion"
                              type="button"
                              onClick={() => handleQuantityChange(item.productId, item.quantity + 1)}
                              disabled={item.quantity >= 99}
                              style={{ minWidth: '30px' }}
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
                  <strong>Итого зелий:</strong> {totalItems} шт.
                </div>
                <div>
                  <strong>Общая сумма:</strong> 
                  <span className="h4 text-potion ms-2">
                    {totalPrice.toFixed(2)} големов
                  </span>
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
            >
              <i className="bi bi-trash me-2"></i>
              Очистить корзину
            </button>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card potion-card mb-4">
            <div className="card-header bg-moonlight border-bottom border-potion">
              <h5 className="mb-0 text-white">
                <i className="bi bi-magic me-2"></i>
                Оформление заказа
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleCreateOrder}>
                <div className="mb-3">
                  <label className="form-label text-moonlight">
                    <i className="bi bi-truck me-1"></i>
                    Способ доставки:
                  </label>
                  <div className="d-flex flex-wrap gap-2">
                    {[
                      { id: 'portal', label: 'Портальная доставка', icon: 'bi-door-closed', desc: 'Мгновенно (1-5 мин)' },
                      { id: 'owl', label: 'Совиная почта', icon: 'bi-send', desc: '1-3 дня' },
                      { id: 'broom', label: 'Метловик', icon: 'bi-airplane', desc: '3-7 дней' },
                      { id: 'pickup', label: 'Самовывоз', icon: 'bi-shop', desc: 'Из лавки' }
                    ].map(method => (
                      <div key={method.id} className="flex-grow-1">
                        <input
                          type="radio"
                          className="btn-check"
                          name="delivery"
                          id={method.id}
                          value={method.id}
                          checked={selectedDelivery === method.id}
                          onChange={(e) => setSelectedDelivery(e.target.value)}
                        />
                        <label 
                          className={`btn btn-sm w-100 ${selectedDelivery === method.id ? 'btn-potion' : 'btn-outline-potion'}`}
                          htmlFor={method.id}
                          title={method.desc}
                        >
                          <i className={`bi ${method.icon} me-1`}></i>
                          {method.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mb-3">
                  <label htmlFor="deliveryAddress" className="form-label text-moonlight">
                    <i className="bi bi-geo-alt me-1"></i>
                    Адрес доставки:
                  </label>
                  <input
                    type="text"
                    className="form-control bg-dark-purple border-potion text-white"
                    id="deliveryAddress"
                    value={orderData.deliveryAddress}
                    onChange={(e) => setOrderData({...orderData, deliveryAddress: e.target.value})}
                    placeholder="Например: Улица Котейная, 13, квартира 7"
                    required
                    style={{ color: '#e6e6ff' }}
                  />
                </div>

                <div className="mb-3">
                  <label htmlFor="phone" className="form-label text-moonlight">
                    <i className="bi bi-telephone me-1"></i>
                    Контактный телефон:
                  </label>
                  <input
                    type="tel"
                    className="form-control bg-dark-purple border-potion text-white"
                    id="phone"
                    value={orderData.phone}
                    onChange={(e) => setOrderData({...orderData, phone: e.target.value})}
                    placeholder="+7 (XXX) XXX-XX-XX"
                    required
                    style={{ color: '#e6e6ff' }}
                  />
                </div>

                <div className="mb-4">
                  <label htmlFor="notes" className="form-label text-moonlight">
                    <i className="bi bi-chat-left-text me-1"></i>
                    Примечания к заказу:
                  </label>
                  <textarea
                    className="form-control bg-dark-purple border-potion text-white"
                    id="notes"
                    rows={3}
                    value={orderData.notes}
                    onChange={(e) => setOrderData({...orderData, notes: e.target.value})}
                    placeholder="Особые пожелания, время доставки, инструкции..."
                    style={{ color: '#e6e6ff' }}
                  />
                </div>

                <div className="card bg-dark-purple border border-potion mb-4">
                  <div className="card-body">
                    <div className="d-flex justify-content-between mb-2">
                      <span>Стоимость зелий:</span>
                      <strong>{totalPrice.toFixed(2)} гол.</strong>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Доставка:</span>
                      <strong>
                        {selectedDelivery === 'portal' ? '500.00 гол.' : 
                         selectedDelivery === 'owl' ? '250.00 гол.' : 
                         selectedDelivery === 'broom' ? '100.00 гол.' : 
                         '0.00 гол.'}
                      </strong>
                    </div>
                    <hr className="border-potion my-2" />
                    <div className="d-flex justify-content-between">
                      <span className="h5 text-moonlight">Итого к оплате:</span>
                      <span className="h4 text-potion">
                        {(
                          totalPrice + 
                          (selectedDelivery === 'portal' ? 500 : 
                           selectedDelivery === 'owl' ? 250 : 
                           selectedDelivery === 'broom' ? 100 : 0)
                        ).toFixed(2)} гол.
                      </span>
                    </div>
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="btn btn-potion btn-lg w-100"
                  disabled={isCreatingOrder || items.length === 0}
                >
                  {isCreatingOrder ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Оформляем заказ...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-bag-check me-2"></i>
                      Оформить заказ
                    </>
                  )}
                </button>

                <p className="text-center text-muted small mt-3">
                  Нажимая кнопку, вы соглашаетесь с правилами магазина
                  <br />и магическими запретами
                </p>
              </form>
            </div>
          </div>

          <div className="card potion-card">
            <div className="card-body">
              <h6 className="text-potion mb-3">
                <i className="bi bi-shield-check me-2"></i>
                Гарантии безопасности
              </h6>
              <ul className="list-unstyled text-muted small">
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-1"></i>
                  Все зелья проходят проверку качества
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-1"></i>
                  Конфиденциальность гарантирована заклинаниями
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-1"></i>
                  Доставка магическими курьерами
                </li>
                <li>
                  <i className="bi bi-check-circle text-success me-1"></i>
                  Возврат в течение 3 лунных циклов
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};