import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface OrderItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

interface Order {
  id: number;
  orderNumber: string;
  createdAt: string;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total: number;
  items: OrderItem[];
  deliveryMethod: string;
  deliveryAddress: string;
}

export const OrdersPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  useEffect(() => {
    const loadOrders = async () => {
      setIsLoading(true);
      try {
        // Имитация загрузки заказов
        await new Promise(resolve => setTimeout(resolve, 1000));
        const mockOrders: Order[] = [
          {
            id: 1,
            orderNumber: 'DM-2024-001',
            createdAt: '2024-01-15',
            status: 'delivered',
            total: 3499.97,
            deliveryMethod: 'portal',
            deliveryAddress: 'Лесная тропа, 7, Хогсмид',
            items: [
              { id: 1, name: 'Зелье Лунного Сияния', price: 1299.99, quantity: 1 },
              { id: 2, name: 'Эликсир Ясного Ума', price: 899.99, quantity: 1 },
              { id: 8, name: 'Любовный Напиток', price: 749.99, quantity: 1 },
            ],
          },
          {
            id: 2,
            orderNumber: 'DM-2024-002',
            createdAt: '2024-01-10',
            status: 'shipped',
            total: 4599.99,
            deliveryMethod: 'owl',
            deliveryAddress: 'Диагон-элли, 12, Лондон',
            items: [
              { id: 9, name: 'Зелье Молодости', price: 4599.99, quantity: 1 }
            ],
          },
          {
            id: 3,
            orderNumber: 'DM-2023-156',
            createdAt: '2023-12-24',
            status: 'cancelled',
            total: 3299.99,
            deliveryMethod: 'portal',
            deliveryAddress: 'Улица Котейная, 13, кв. 7',
            items: [
              { id: 4, name: 'Оборотное Зелье', price: 3299.99, quantity: 1 }
            ],
          }
        ];
        setOrders(mockOrders);
      } catch (error) {
        console.error('Ошибка загрузки заказов:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      loadOrders();
    }
  }, [user]);

  const getStatusInfo = (status: Order['status']) => {
    switch (status) {
      case 'pending': return { label: 'Ожидает обработки', color: 'warning', icon: 'bi-clock' };
      case 'processing': return { label: 'В обработке', color: 'info', icon: 'bi-gear' };
      case 'shipped': return { label: 'Отправлен', color: 'primary', icon: 'bi-truck' };
      case 'delivered': return { label: 'Доставлен', color: 'success', icon: 'bi-check-circle' };
      case 'cancelled': return { label: 'Отменен', color: 'danger', icon: 'bi-x-circle' };
      default: return { label: 'Неизвестно', color: 'secondary', icon: 'bi-question-circle' };
    }
  };

  const getDeliveryInfo = (method: string) => {
    switch (method) {
      case 'owl': return { label: 'Сова', icon: 'bi bi-bird' };
      case 'broom': return { label: 'Метла', icon: 'bi bi-wand' };
      case 'portal': return { label: 'Портал', icon: 'bi bi-stars' };
      default: return { label: 'Неизвестно', icon: 'bi bi-question-circle' };
    }
  };

  if (!user) {
    return (
      <div className="container py-5">
        <div className="text-center py-5">
          <div className="mb-4">
            <i className="bi bi-person-lock display-1 text-potion"></i>
          </div>
          <h2 className="mb-4">Доступ к заказам ограничен</h2>
          <p className="lead mb-4">Для доступа к истории заказов необходимо войти в магический аккаунт</p>
          <div className="d-flex justify-content-center gap-3">
            <button 
              className="btn btn-potion btn-lg"
              onClick={() => navigate('/login')}
            >
              <i className="bi bi-key me-2"></i>Войти
            </button>
            <button 
              className="btn btn-outline-potion btn-lg"
              onClick={() => navigate('/register')}
            >
              <i className="bi bi-person-plus me-2"></i>Зарегистрироваться
            </button>
          </div>
        </div>
      </div>
    );
  }

  const filteredOrders = selectedStatus === 'all' ? orders : orders.filter(order => order.status === selectedStatus);

  return (
    <div className="py-5">
      <h1 className="mb-4 text-potion"><i className="bi bi-bag-check me-3"></i>Мои заказы</h1>
      <div className="row mb-4">
        <div className="col-md-3 col-6 mb-3">
          <div className="card potion-card text-center">
            <div className="card-body">
              <div className="h2 text-success">{orders.filter(o => o.status === 'delivered').length}</div>
              <div className="text-muted">Доставлено</div>
            </div>
          </div>
        </div>
        <div className="col-md-3 col-6 mb-3">
          <div className="card potion-card text-center">
            <div className="card-body">
              <div className="h2 text-primary">{orders.filter(o => o.status === 'shipped').length}</div>
              <div className="text-muted">В пути</div>
            </div>
          </div>
        </div>
        <div className="col-md-3 col-6 mb-3">
          <div className="card potion-card text-center">
            <div className="card-body">
              <div className="h2 text-info">{orders.filter(o => o.status === 'processing' || o.status === 'shipped').length}</div>
              <div className="text-muted">В процессе</div>
            </div>
          </div>
        </div>
        <div className="col-md-3 col-6 mb-3">
          <div className="card potion-card text-center">
            <div className="card-body">
              <div className="h2 text-danger">{orders.filter(o => o.status === 'cancelled').length}</div>
              <div className="text-muted">Отменено</div>
            </div>
          </div>
        </div>
      </div>

      {/* Фильтры */}
      <div className="card potion-card mb-4">
        <div className="card-body">
          <div className="d-flex flex-wrap align-items-center justify-content-between">
            <h5 className="mb-0"><i className="bi bi-funnel me-2"></i>Фильтры</h5>
            <select
              className="form-select bg-dark-purple border-potion text-white"
              style={{ maxWidth: '200px', color: '#e6e6ff' }}
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
            >
              <option value="all">Все статусы</option>
              <option value="pending">Ожидает</option>
              <option value="processing">Обрабатывается</option>
              <option value="shipped">Отправлен</option>
              <option value="delivered">Доставлен</option>
              <option value="cancelled">Отменен</option>
            </select>
          </div>
        </div>
      </div>

      {/* Список заказов */}
      <div className="row g-4">
        {isLoading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-potion" role="status">
              <span className="visually-hidden">Загрузка...</span>
            </div>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="text-center py-5">
            <div className="mb-4">
              <i className="bi bi-bag-plus display-1 text-potion"></i>
            </div>
            <h3 className="mb-3">Сделайте ваш первый заказ!</h3>
            <p className="text-muted mb-4">Ваши магические покупки будут отображаться здесь.</p>
            <div className="d-flex flex-wrap gap-3 justify-content-center">
              <Link to="/potions" className="btn btn-potion btn-lg">
                <i className="bi bi-flask me-2"></i>Каталог зелий
              </Link>
              <Link to="/" className="btn btn-outline-potion btn-lg">
                <i className="bi bi-star me-2"></i>Популярные зелья
              </Link>
            </div>
          </div>
        ) : (
          filteredOrders.map((order) => {
            const statusInfo = getStatusInfo(order.status);
            const deliveryInfo = getDeliveryInfo(order.deliveryMethod);

            return (
              <div key={order.id} className="col-lg-6">
                <div className="card potion-card h-100">
                  <div className="card-header bg-moonlight border-bottom border-potion d-flex justify-content-between align-items-center">
                    <h5 className="mb-0 text-white">
                      <i className={`bi ${statusInfo.icon} me-2 text-${statusInfo.color}`}></i>
                      {order.orderNumber}
                    </h5>
                    <span className={`badge bg-${statusInfo.color}`}>
                      {statusInfo.label}
                    </span>
                  </div>
                  <div className="card-body">
                    <div className="row mb-3">
                      <div className="col-md-6">
                        <ul className="list-unstyled text-moonlight">
                          <li className="mb-2"><i className="bi bi-hash me-2"></i><strong>Номер заказа:</strong> {order.orderNumber}</li>
                          <li className="mb-2"><i className="bi bi-calendar me-2"></i><strong>Дата создания:</strong> {order.createdAt}</li>
                          <li className="mb-2"><i className={`bi ${deliveryInfo.icon} me-2`}></i><strong>Способ доставки:</strong> {deliveryInfo.label}</li>
                          <li><i className="bi bi-geo-alt me-2"></i><strong>Адрес:</strong> {order.deliveryAddress}</li>
                        </ul>
                      </div>
                      <div className="col-md-6">
                        <h6 className="text-potion mb-3"><i className="bi bi-flask me-2"></i>Состав заказа</h6>
                        <ul className="list-group list-group-flush">
                          {order.items.map((item) => (
                            <li key={item.id} className="list-group-item bg-transparent text-muted py-1 border-0 ps-0">
                              {item.quantity}x {item.name} - {(item.price * item.quantity).toFixed(2)} гол.
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="d-flex justify-content-between align-items-center mt-auto">
                      <div>
                        <strong className="text-potion">Итого: {order.total.toFixed(2)} гол.</strong>
                      </div>
                      <div>
                        <button className="btn btn-sm btn-outline-danger me-2">
                          <i className="bi bi-x-circle me-1"></i>Отменить заказ
                        </button>
                        <button className="btn btn-sm btn-outline-potion">
                          <i className="bi bi-question-circle me-1"></i>Помощь
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default OrdersPage;