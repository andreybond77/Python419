import React, { useState, useEffect, useCallback } from 'react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { mockPotions } from '../mockData';
import { Potion } from '../types';

export const PotionsPage: React.FC = () => {
  const [potions] = useState<Potion[]>(mockPotions);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedRarity, setSelectedRarity] = useState<string>('all');
  const [imageErrors, setImageErrors] = useState<{ [key: number]: boolean }>({});
  const [notification, setNotification] = useState<string | null>(null);

  const { addToCart } = useCart();
  const { user } = useAuth();

  // Эффект для автоматического скрытия уведомления
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const categories = [
    { value: 'all', label: 'Все зелья', icon: 'bi-flask', color: '#9d4edd' },
    { value: 'physical', label: 'Физические', icon: 'bi-activity', color: '#ff6b6b' },
    { value: 'mental', label: 'Психические', icon: 'bi-brain', color: '#4dffea' },
    { value: 'healing', label: 'Целительные', icon: 'bi-heart-pulse', color: '#38b000' },
    { value: 'transformative', label: 'Преображающие', icon: 'bi-magic', color: '#ff9e00' },
    { value: 'protective', label: 'Защитные', icon: 'bi-shield-check', color: '#4361ee' },
    { value: 'combat', label: 'Боевые', icon: 'bi-fire', color: '#f72585' },
    { value: 'poison', label: 'Яды', icon: 'bi-skull', color: '#6a040f' }
  ];

  const rarities = [
    { value: 'all', label: 'Все редкости', color: '#6c757d' },
    { value: 'common', label: 'Обычные', color: '#6c757d' },
    { value: 'rare', label: 'Редкие', color: '#0d6efd' },
    { value: 'epic', label: 'Эпические', color: '#6f42c1' },
    { value: 'legendary', label: 'Легендарные', color: '#fd7e14' }
  ];

  const getRarityLabel = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'Обычное';
      case 'rare': return 'Редкое';
      case 'epic': return 'Эпическое';
      case 'legendary': return 'Легендарное';
      default: return 'Неизвестно';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'physical': return 'Физическое';
      case 'mental': return 'Психическое';
      case 'healing': return 'Целительное';
      case 'transformative': return 'Преображающее';
      case 'protective': return 'Защитное';
      case 'combat': return 'Боевое';
      case 'poison': return 'Яд';
      default: return 'Неизвестно';
    }
  };

  const getCategoryColor = (category: string) => {
    const categoryInfo = categories.find(c => c.value === category);
    return categoryInfo?.color || '#9d4edd';
  };

  const getFallbackImage = (potionName: string, category: string, rarity: string) => {
    const color = getCategoryColor(category);
    const rarityColor = rarities.find(r => r.value === rarity)?.color || '#6c757d';
    
    return `data:image/svg+xml,${encodeURIComponent(`
      <svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200">
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
        <rect x="110" y="50" width="80" height="100" rx="5" fill="url(#bottleGradient)" stroke="${color}" stroke-width="3"/>
        <rect x="120" y="40" width="60" height="10" rx="3" fill="${color}" opacity="0.9"/>
        <rect x="130" y="155" width="40" height="10" rx="2" fill="${color}" opacity="0.7"/>
        <circle cx="140" cy="80" r="10" fill="white" opacity="0.4"/>
        <circle cx="160" cy="95" r="8" fill="white" opacity="0.5"/>
        <circle cx="150" cy="120" r="12" fill="white" opacity="0.3"/>
      </svg>
    `)}`;
  };

  const handleImageError = (potionId: number) => {
    setImageErrors(prev => ({ ...prev, [potionId]: true }));
  };

  const handleAddToCart = useCallback((potion: Potion) => {
    console.log('Добавление в корзину:', potion.name);
    
    if (!user) {
      setNotification('Для покупки магических зелий необходимо войти в аккаунт.');
      return;
    }
    
    if (!potion.in_stock) {
      setNotification(`${potion.name} временно отсутствует в наличии.`);
      return;
    }

    try {
      if (!addToCart || typeof addToCart !== 'function') {
        setNotification('Ошибка: функция корзины недоступна');
        return;
      }
      
      addToCart(potion);
      setNotification(`${potion.name} добавлено в корзину!`);
      console.log('Товар успешно добавлен:', potion.name);
      
    } catch (error) {
      console.error('Ошибка при добавлении в корзину:', error);
      setNotification('Ошибка при добавлении в корзину. Попробуйте снова.');
    }
  }, [user, addToCart]);

  const filteredPotions = potions.filter(potion => {
    const matchesSearch = potion.name.toLowerCase().includes(search.toLowerCase()) ||
                          potion.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || potion.category === selectedCategory;
    const matchesRarity = selectedRarity === 'all' || potion.rarity === selectedRarity;
    return matchesSearch && matchesCategory && matchesRarity;
  });

  return (
    <div className="potions-page-background">
      <div className="container py-5">
        {/* Простое уведомление */}
        {notification && (
          <div 
            className="alert alert-success position-fixed top-0 end-0 m-3 shadow-lg"
            style={{
              zIndex: 9999,
              minWidth: '300px',
              animation: 'fadeIn 0.3s ease-in-out'
            }}
            role="alert"
          >
            <div className="d-flex align-items-center">
              <i className="bi bi-check-circle-fill me-2"></i>
              <span className="flex-grow-1">{notification}</span>
              <button 
                type="button" 
                className="btn-close ms-2" 
                onClick={() => setNotification(null)}
                aria-label="Close"
              ></button>
            </div>
          </div>
        )}

        {/* Заголовок */}
        <div className="text-center mb-5 content-overlay">
          <h1 className="section-title text-over-background">
            <i className="bi bi-flask me-3"></i>
            Каталог Магических Зелий
          </h1>
          <p className="section-subtitle text-over-background">
            Откройте для себя древние рецепты и могущественные эликсиры
          </p>
        </div>

        {/* Фильтры */}
        <div className="card potion-card glass-effect mb-4">
          <div className="card-body">
            <div className="row g-3">
              <div className="col-md-6">
                <div className="input-group input-group-lg">
                  <span className="input-group-text bg-transparent border-potion text-white">
                    <i className="bi bi-search text-potion"></i>
                  </span>
                  <input
                    type="text"
                    className="form-control bg-transparent border-potion text-white"
                    placeholder="Поиск зелий по названию или эффектам..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    style={{ color: '#e6e6ff' }}
                  />
                </div>
              </div>
              <div className="col-md-3">
                <select
                  className="form-select form-select-lg bg-transparent border-potion text-white"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  style={{ color: '#e6e6ff' }}
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-3">
                <select
                  className="form-select form-select-lg bg-transparent border-potion text-white"
                  value={selectedRarity}
                  onChange={(e) => setSelectedRarity(e.target.value)}
                  style={{ color: '#e6e6ff' }}
                >
                  {rarities.map(rar => (
                    <option key={rar.value} value={rar.value}>{rar.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="mt-4 pt-3 border-top border-potion">
              <div className="d-flex flex-wrap gap-2 mb-2">
                <small className="text-moonlight me-2">Категории:</small>
                {categories.slice(1).map(category => (
                  <button
                    key={category.value}
                    className={`btn ${selectedCategory === category.value ? 'btn-potion' : 'btn-outline-potion'} btn-sm`}
                    onClick={() => setSelectedCategory(category.value)}
                    type="button"
                    style={{
                      borderColor: category.color,
                      color: selectedCategory === category.value ? 'white' : category.color
                    }}
                  >
                    <i className={`bi ${category.icon} me-2`}></i>
                    {category.label}
                  </button>
                ))}
                <button
                  className="btn btn-outline-secondary btn-sm"
                  onClick={() => {
                    setSearch('');
                    setSelectedCategory('all');
                    setSelectedRarity('all');
                  }}
                  type="button"
                >
                  <i className="bi bi-arrow-clockwise me-2"></i>
                  Сбросить
                </button>
              </div>
              <div className="d-flex align-items-center mt-2">
                <span className="text-moonlight me-3">
                  <i className="bi bi-filter-circle me-2"></i>
                  Найдено зелий: <strong>{filteredPotions.length}</strong> из {potions.length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Карточки зелий */}
        {filteredPotions.length === 0 ? (
          <div className="text-center py-5 content-overlay rounded-4">
            <div className="mb-4">
              <i className="bi bi-flask display-1 text-muted"></i>
            </div>
            <h3 className="text-moonlight mb-3">Зелья не найдены</h3>
            <p className="text-muted mb-4">
              Попробуйте изменить параметры поиска или выберите другую категорию
            </p>
            <button
              className="btn btn-outline-potion"
              onClick={() => {
                setSearch('');
                setSelectedCategory('all');
                setSelectedRarity('all');
              }}
              type="button"
            >
              <i className="bi bi-arrow-clockwise me-2"></i>
              Показать все зелья
            </button>
          </div>
        ) : (
          <div className="grid-container">
            {filteredPotions.map(potion => {
              const categoryInfo = categories.find(c => c.value === potion.category) || categories[0];
              const rarityInfo = rarities.find(r => r.value === potion.rarity) || rarities[0];
              const fallbackImage = getFallbackImage(potion.name, potion.category, potion.rarity);

              return (
                <div key={`potion-${potion.id}`} className="grid-item glass-effect">
                  <div className="character-card">
                    <div className="category-tag" style={{
                      backgroundColor: `${categoryInfo.color}30`,
                      borderColor: categoryInfo.color,
                      color: 'white'
                    }}>
                      {categoryInfo.label}
                    </div>
                    <div className="card-badge" style={{
                      backgroundColor: rarityInfo.color,
                      color: 'white'
                    }}>
                      {getRarityLabel(potion.rarity)}
                    </div>
                    <div className="card-image-wrapper">
                      <img
                        src={imageErrors[potion.id] ? fallbackImage : potion.image_url}
                        alt={potion.name}
                        className="card-image"
                        onError={() => handleImageError(potion.id)}
                        loading="lazy"
                      />
                    </div>
                    <div className="card-content">
                      <h5 className="card-title">{potion.name}</h5>
                      <p className="card-description">{potion.description}</p>
                      <div className="card-details">
                        <div className="d-flex flex-column">
                          <span>
                            <i className="bi bi-clock me-1"></i>
                            {potion.brewing_time}
                          </span>
                          <span>
                            <i className="bi bi-droplet me-1"></i>
                            {potion.ingredients.length} ингредиентов
                          </span>
                        </div>
                        <div className={`status-indicator ${potion.in_stock ? 'status-in-stock' : 'status-out-of-stock'}`}>
                          <i className={`bi ${potion.in_stock ? 'bi-check-circle' : 'bi-clock-history'}`}></i>
                          {potion.in_stock ? 'В наличии' : 'Под заказ'}
                        </div>
                      </div>
                      <div className="mb-3">
                        <div className="d-flex flex-wrap gap-2">
                          {potion.effects.slice(0, 2).map((effect, index) => (
                            <span
                              key={`effect-${potion.id}-${index}`}
                              className="badge bg-dark border border-potion text-potion small"
                              style={{ fontSize: '0.7rem' }}
                            >
                              {effect}
                            </span>
                          ))}
                          {potion.effects.length > 2 && (
                            <span className="badge bg-secondary small" style={{ fontSize: '0.7rem' }}>
                              +{potion.effects.length - 2} эффектов
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="mt-auto">
                        <div className="d-flex justify-content-between align-items-center mb-3">
                          <div className="card-price">
                            {potion.price.toFixed(2)} <small className="text-muted">гол.</small>
                          </div>
                        </div>
                        <button
                          onClick={() => handleAddToCart(potion)}
                          className={`card-button ${potion.in_stock ? 'btn-potion' : 'btn-secondary'}`}
                          disabled={!potion.in_stock || !user}
                          type="button"
                        >
                          {!potion.in_stock ? (
                            <>
                              <i className="bi bi-clock me-1"></i>
                              Предзаказ
                            </>
                          ) : !user ? (
                            <>
                              <i className="bi bi-lock me-1"></i>
                              Войти для покупки
                            </>
                          ) : (
                            <>
                              <i className="bi bi-cart-plus me-1"></i>
                              В корзину
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Статистика */}
        {filteredPotions.length > 0 && (
          <div className="mt-5 pt-4 border-top border-potion">
            <div className="row text-center">
              <div className="col-md-3 col-6 mb-3">
                <div className="p-3 potion-card glass-effect">
                  <div className="h4 text-potion mb-2">{filteredPotions.length}</div>
                  <div className="text-muted small">Показано зелий</div>
                </div>
              </div>
              <div className="col-md-3 col-6 mb-3">
                <div className="p-3 potion-card glass-effect">
                  <div className="h4 text-success mb-2">
                    {filteredPotions.filter(p => p.in_stock).length}
                  </div>
                  <div className="text-muted small">В наличии</div>
                </div>
              </div>
              <div className="col-md-3 col-6 mb-3">
                <div className="p-3 potion-card glass-effect">
                  <div className="h4 text-moonlight mb-2">
                    {filteredPotions.filter(p => p.rarity === 'legendary').length}
                  </div>
                  <div className="text-muted small">Легендарных</div>
                </div>
              </div>
              <div className="col-md-3 col-6 mb-3">
                <div className="p-3 potion-card glass-effect">
                  <div className="h4 text-warning mb-2">
                    ${filteredPotions.reduce((sum, p) => sum + p.price, 0).toFixed(2)}
                  </div>
                  <div className="text-muted small">Общая стоимость</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PotionsPage;