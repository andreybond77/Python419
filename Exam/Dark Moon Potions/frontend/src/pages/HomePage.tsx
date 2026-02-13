import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

export const HomePage: React.FC = () => {
  const { user } = useAuth();
  const { totalItems } = useCart();

  const categories = [
    { name: 'Физические', icon: 'bi-activity', color: '#ff6b6b', count: 12, description: 'Влияют на физическое состояние' },
    { name: 'Психические', icon: 'bi-brain', color: '#4dffea', count: 8, description: 'Влияют на психику и эмоции' },
    { name: 'Целительные', icon: 'bi-heart-pulse', color: '#38b000', count: 15, description: 'Исцеляют раны и болезни' },
    { name: 'Преображающие', icon: 'bi-magic', color: '#ff9e00', count: 5, description: 'Изменяют внешность и свойства' },
    { name: 'Защитные', icon: 'bi-shield-check', color: '#4361ee', count: 10, description: 'Защита от магии и атак' },
    { name: 'Боевые', icon: 'bi-fire', color: '#f72585', count: 7, description: 'Используются в бою' },
    { name: 'Яды', icon: 'bi-skull', color: '#6a040f', count: 3, description: 'Смертельные отравы' },
  ];

  const featuredPotions = [
    { id: 1, name: 'Зелье Лунного Сияния', category: 'Физические', price: 1299.99, rarity: 'Эпическое', description: 'Дает силу и выносливость под светом луны', image: '/src/images/potion_1.webp' },
    { id: 2, name: 'Эликсир Ясного Ума', category: 'Психические', price: 899.99, rarity: 'Редкое', description: 'Улучшает концентрацию и память', image: '/src/images/potion_2.webp' },
    { id: 3, name: 'Бальзам Феникса', category: 'Целительные', price: 2499.99, rarity: 'Легендарное', description: 'Заживляет любые раны и восстанавливает энергию', image: '/src/images/potion_10.webp' },
    { id: 8, name: 'Зелье Молодости', category: 'Преображающие', price: 4599.99, rarity: 'Легендарное', description: 'Временно возвращает молодость и жизненные силы', image: '/src/images/potion_30.webp' },
  ];

  // Функция для создания fallback изображения
  const createFallbackImage = (potionName: string, category: string, rarity: string, price: number) => {
    const colors: Record<string, string> = {
      'Физические': '#ff6b6b',
      'Психические': '#4dffea',
      'Целительные': '#38b000',
      'Преображающие': '#ff9e00',
      'Защитные': '#4361ee',
      'Боевые': '#f72585',
      'Яды': '#6a040f'
    };
    
    const rarityColors: Record<string, string> = {
      'Обычное': '#6c757d',
      'Редкое': '#0d6efd',
      'Эпическое': '#6f42c1',
      'Легендарное': '#dc3545'
    };
    
    const color = colors[category] || '#9d4edd';
    const rarityColor = rarityColors[rarity] || '#6c757d';
    
    return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200">
      <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${color};stop-opacity:0.3" />
          <stop offset="100%" style="stop-color:#1a0033;stop-opacity:0.9" />
        </linearGradient>
        <linearGradient id="bottleGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:${color};stop-opacity:0.9" />
          <stop offset="100%" style="stop-color:${rarityColor};stop-opacity:0.8" />
        </linearGradient>
      </defs>
      <rect width="300" height="200" fill="url(#bgGradient)" />
      
      <!-- Бутылка зелья -->
      <rect x="110" y="50" width="80" height="100" rx="5" fill="url(#bottleGradient)" stroke="${color}" stroke-width="3"/>
      <rect x="120" y="40" width="60" height="10" rx="3" fill="${color}" opacity="0.9"/>
      <rect x="130" y="155" width="40" height="10" rx="2" fill="${color}" opacity="0.7"/>
      
      <!-- Пузырьки -->
      <circle cx="140" cy="80" r="10" fill="white" opacity="0.4"/>
      <circle cx="160" cy="95" r="8" fill="white" opacity="0.5"/>
      <circle cx="150" cy="120" r="12" fill="white" opacity="0.3"/>
      
      <!-- Название и цена -->
      <text x="150" y="190" text-anchor="middle" fill="white" font-family="Arial" font-size="14" font-weight="bold" filter="url(#shadow)">
        ${potionName}
      </text>
      <text x="150" y="175" text-anchor="middle" fill="${color}" font-family="Arial" font-size="12" font-weight="bold">
        ${category} • ${rarity}
      </text>
      <text x="150" y="25" text-anchor="middle" fill="white" font-family="Arial" font-size="16" font-weight="bold" filter="url(#shadow)">
        ${price.toFixed(2)} гол.
      </text>
      <defs>
        <filter id="shadow">
          <feDropShadow dx="1" dy="1" stdDeviation="2" flood-color="#000" flood-opacity="0.7"/>
        </filter>
      </defs>
    </svg>`;
  };

  return (
    <div className="home-page-background">
      {/* Герой секция с фоном */}
      <section className="home-page-hero">
        <div className="container py-5">
          <div className="text-center mb-5 content-overlay float-effect">
            <div className="mb-4">
              <i className="bi bi-flask display-1 text-potion glow-border rounded-circle p-4"></i>
            </div>
            <h1 className="display-3 text-potion mb-3 fw-bold">Dark Moon Potions</h1>
            <p className="lead text-moonlight fs-4 mb-4">
              Откройте для себя мир мощных и загадочных магических зелий.
              <br />Созданные из редчайших ингредиентов мастерами зельеварения.
            </p>
            <div className="d-flex flex-wrap gap-3 justify-content-center mt-4">
              <Link to="/potions" className="btn btn-potion btn-lg px-5 py-3">
                <i className="bi bi-flask me-2"></i>
                Смотреть зелья
              </Link>
              {user ? (
                <Link to="/cart" className="btn btn-outline-potion btn-lg px-5 py-3 position-relative">
                  <i className="bi bi-basket me-2"></i>
                  Корзина
                  {totalItems > 0 && (
                    <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                      {totalItems}
                    </span>
                  )}
                </Link>
              ) : (
                <Link to="/login" className="btn btn-outline-potion btn-lg px-5 py-3">
                  <i className="bi bi-key me-2"></i>
                  Войти в магазин
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Основной контент */}
      <div className="container py-5">
        {/* Статистика */}
        <div className="row mb-5">
          <div className="col-md-3 col-6 mb-3">
            <div className="card potion-card text-center card-overlay">
              <div className="card-body">
                <div className="h1 text-potion mb-2 fw-bold">32</div>
                <div className="text-muted fs-5">Уникальных зелий</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-6 mb-3">
            <div className="card potion-card text-center card-overlay">
              <div className="card-body">
                <div className="h1 text-moonlight mb-2 fw-bold">7</div>
                <div className="text-muted fs-5">Категорий</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-6 mb-3">
            <div className="card potion-card text-center card-overlay">
              <div className="card-body">
                <div className="h1 text-success mb-2 fw-bold">100%</div>
                <div className="text-muted fs-5">Натуральные ингредиенты</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-6 mb-3">
            <div className="card potion-card text-center card-overlay">
              <div className="card-body">
                <div className="h1 text-warning mb-2 fw-bold">24/7</div>
                <div className="text-muted fs-5">Магическая поддержка</div>
              </div>
            </div>
          </div>
        </div>

        {/* Популярные зелья */}
        <section className="mb-5 section-with-bg glass-effect">
          <div className="container">
            <h2 className="section-title">
              <i className="bi bi-fire me-3"></i>
              Популярные зелья
            </h2>
            <p className="section-subtitle mb-4">
              Самые востребованные и могущественные эликсиры от наших мастеров
            </p>
            <div className="grid-container">
              {featuredPotions.map((potion) => (
                <div key={potion.id} className="grid-item glass-effect">
                  <div className="character-card">
                    {/* Бейдж редкости */}
                    <div className="card-badge" style={{
                      backgroundColor: potion.rarity === 'Легендарное' ? '#dc3545' : 
                                     potion.rarity === 'Эпическое' ? '#6f42c1' : '#0d6efd',
                      color: 'white'
                    }}>
                      {potion.rarity}
                    </div>

                    {/* Изображение */}
                    <div className="card-image-wrapper">
                      <img 
                        src={potion.image}
                        className="card-image"
                        alt={potion.name}
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.onerror = null;
                          target.src = createFallbackImage(potion.name, potion.category, potion.rarity, potion.price);
                        }}
                        loading="lazy"
                      />
                    </div>

                    {/* Контент карточки */}
                    <div className="card-content">
                      <h5 className="card-title">{potion.name}</h5>
                      <p className="card-description">
                        {potion.description}
                      </p>
                      <div className="mb-3">
                        <span className="badge bg-dark border border-potion">{potion.category}</span>
                      </div>
                      <div className="mt-auto">
                        <div className="card-price mb-3">{potion.price.toFixed(2)} големов</div>
                        <Link to="/potions" className="btn btn-outline-potion w-100">
                          <i className="bi bi-eye me-2"></i>
                          Подробнее
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="text-center mt-4">
              <Link to="/potions" className="btn btn-potion btn-lg">
                Посмотреть все зелья <i className="bi bi-arrow-right ms-2"></i>
              </Link>
            </div>
          </div>
        </section>

        {/* Категории */}
        <section className="mb-5 section-with-bg glass-effect">
          <div className="container">
            <h2 className="section-title">
              <i className="bi bi-grid-3x3-gap me-3"></i>
              Категории зелий
            </h2>
            <p className="section-subtitle mb-4">
              Выберите подходящий тип магических эликсиров для ваших нужд
            </p>
            <div className="grid-container">
              {categories.map((category, index) => (
                <div key={index} className="grid-item glass-effect">
                  <div className="character-card text-center h-100">
                    <div className="card-content d-flex flex-column align-items-center justify-content-center">
                      <div 
                        className="rounded-circle mb-4 d-flex align-items-center justify-content-center"
                        style={{ 
                          width: '80px', 
                          height: '80px', 
                          backgroundColor: `${category.color}30`,
                          border: `3px solid ${category.color}`,
                          boxShadow: `0 0 15px ${category.color}50`
                        }}
                      >
                        <i 
                          className={`bi ${category.icon} display-5`} 
                          style={{ color: category.color }}
                        ></i>
                      </div>
                      <h3 className="card-title mb-2">{category.name}</h3>
                      <p className="card-description mb-3">{category.description}</p>
                      <span className="badge bg-dark border border-potion mt-auto">{category.count} зелий</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* О нас */}
        <section className="mb-5">
          <div className="row align-items-center">
            <div className="col-lg-6 mb-4 mb-lg-0">
              <div className="p-4 potion-card glass-effect h-100">
                <h2 className="text-potion mb-3">
                  <i className="bi bi-stars me-2"></i>
                  О нашем магазине
                </h2>
                <p className="text-moonlight fs-5">
                  Dark Moon Potions — это легендарный магазин магических зелий, существующий с XV века. 
                  Наши рецепты передаются из поколения в поколение, а ингредиенты собираются в самых 
                  таинственных уголках магического мира.
                </p>
                <ul className="list-unstyled text-moonlight fs-5">
                  <li className="mb-2"><i className="bi bi-check-circle text-success me-2"></i> Сертифицированные мастера-зельевары</li>
                  <li className="mb-2"><i className="bi bi-check-circle text-success me-2"></i> 100% натуральные ингредиенты</li>
                  <li className="mb-2"><i className="bi bi-check-circle text-success me-2"></i> Конфиденциальность гарантирована</li>
                  <li><i className="bi bi-check-circle text-success me-2"></i> Доставка по всему миру через порталы</li>
                </ul>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="p-4 potion-card text-center glass-effect h-100">
                <h3 className="text-potion mb-4">Наши преимущества</h3>
                <div className="row">
                  <div className="col-6 mb-3">
                    <div className="p-3">
                      <i className="bi bi-shield-check display-4 text-potion mb-3"></i>
                      <h5>Безопасность</h5>
                      <p className="small text-muted">Все зелья проходят тестирование</p>
                    </div>
                  </div>
                  <div className="col-6 mb-3">
                    <div className="p-3">
                      <i className="bi bi-gem display-4 text-potion mb-3"></i>
                      <h5>Качество</h5>
                      <p className="small text-muted">Только высший сорт ингредиентов</p>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="p-3">
                      <i className="bi bi-clock-history display-4 text-potion mb-3"></i>
                      <h5>Традиции</h5>
                      <p className="small text-muted">500 лет магического опыта</p>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="p-3">
                      <i className="bi bi-headset display-4 text-potion mb-3"></i>
                      <h5>Поддержка</h5>
                      <p className="small text-muted">Круглосуточная магическая помощь</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="text-center p-5 potion-card glow-effect glass-effect">
          <h2 className="section-title mb-3">Готовы начать?</h2>
          <p className="section-subtitle mb-4">
            Присоединяйтесь к тысячам довольных волшебников по всему миру
          </p>
          {!user ? (
            <div className="d-flex flex-wrap gap-3 justify-content-center">
              <Link to="/register" className="btn btn-potion btn-lg px-4">
                <i className="bi bi-person-plus me-2"></i>
                Создать аккаунт
              </Link>
              <Link to="/potions" className="btn btn-outline-potion btn-lg px-4">
                <i className="bi bi-eye me-2"></i>
                Посмотреть каталог
              </Link>
            </div>
          ) : (
            <Link to="/potions" className="btn btn-potion btn-lg px-5">
              <i className="bi bi-flask me-2"></i>
              Перейти к покупкам
            </Link>
          )}
        </section>
      </div>
    </div>
  );
};

export default HomePage;