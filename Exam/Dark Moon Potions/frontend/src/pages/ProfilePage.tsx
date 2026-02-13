import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProfileData {
  name: string;
  email: string;
  address: string;
  bio: string;
}

export const ProfilePage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState<ProfileData>({
    name: user?.name || '',
    email: user?.email || '',
    address: user?.address || '',
    bio: user?.bio || '',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    if (user) {
      setProfileData({
        name: user.name,
        email: user.email,
        address: user.address || '',
        bio: user.bio || '',
      });
    }
  }, [user]);

  const getWizardLevelInfo = (level: string) => {
    switch (level) {
      case 'novice':
        return { label: 'Новичок', color: 'primary', icon: 'bi-star', desc: 'Только начинает путь' };
      case 'apprentice':
        return { label: 'Ученик', color: 'secondary', icon: 'bi-book', desc: 'Изучает основы' };
      case 'adept':
        return { label: 'Адепт', color: 'success', icon: 'bi-lightning', desc: 'Уверенно владеет магией' };
      case 'master':
        return { label: 'Мастер', color: 'warning', icon: 'bi-trophy', desc: 'Магистр зельеварения' };
      case 'archmage':
        return { label: 'Архимаг', color: 'danger', icon: 'bi-fire', desc: 'Великий волшебник' };
      default:
        return { label: 'Неизвестно', color: 'secondary', icon: 'bi-question-circle', desc: '' };
    }
  };

  const handleSaveProfile = () => {
    // Имитация сохранения профиля
    setIsEditing(false);
    alert('Профиль успешно обновлен!');
  };

  if (!user) {
    return (
      <div className="container py-5">
        <div className="text-center py-5">
          <div className="mb-4">
            <i className="bi bi-person-lock display-1 text-potion"></i>
          </div>
          <h2 className="mb-4">Доступ ограничен</h2>
          <p className="lead mb-4">Для просмотра профиля необходимо войти в аккаунт</p>
          <div className="d-flex justify-content-center gap-3">
            <Link to="/login" className="btn btn-potion btn-lg">
              <i className="bi bi-key me-2"></i>Войти
            </Link>
            <Link to="/register" className="btn btn-outline-potion btn-lg">
              <i className="bi bi-person-plus me-2"></i>Регистрация
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const wizardInfo = getWizardLevelInfo(user.wizardLevel);

  return (
    <div className="py-5">
      <h1 className="mb-4 text-potion"><i className="bi bi-person-circle me-3"></i>Магический профиль</h1>
      <div className="row">
        {/* Левая колонка - информация профиля */}
        <div className="col-lg-4 mb-4">
          <div className="card potion-card">
            <div className="card-body text-center">
              {/* Аватар */}
              <div className="mb-4">
                <div className="rounded-circle mx-auto d-flex align-items-center justify-content-center" style={{
                  width: '150px',
                  height: '150px',
                  background: 'linear-gradient(135deg, #9d4edd 0%, #5a189a 100%)',
                  color: 'white',
                  fontSize: '60px',
                  marginBottom: '20px'
                }}>
                  <i className="bi bi-person-fill"></i>
                </div>
                <h3 className="text-moonlight mb-2">{profileData.name}</h3>
                <div className={`badge bg-${wizardInfo.color} rounded-pill`}>
                  <i className={`bi ${wizardInfo.icon} me-1`}></i>
                  {wizardInfo.label}
                </div>
              </div>

              {/* Навигация по вкладкам */}
              <div className="nav flex-column nav-pills mb-4">
                <button className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
                  <i className="bi bi-person me-2"></i> Профиль
                </button>
                <button className={`nav-link ${activeTab === 'security' ? 'active' : ''}`} onClick={() => setActiveTab('security')}>
                  <i className="bi bi-shield-lock me-2"></i> Безопасность
                </button>
                <button className={`nav-link ${activeTab === 'notifications' ? 'active' : ''}`} onClick={() => setActiveTab('notifications')}>
                  <i className="bi bi-bell me-2"></i> Уведомления
                </button>
              </div>

              {/* Кнопка выхода */}
              <button className="btn btn-outline-danger w-100" onClick={logout}>
                <i className="bi bi-box-arrow-right me-2"></i> Выйти
              </button>
            </div>
          </div>
        </div>

        {/* Правая колонка - контент вкладок */}
        <div className="col-lg-8">
          <div className="card potion-card">
            <div className="card-body">
              {activeTab === 'profile' && (
                <div>
                  <h5 className="text-potion mb-4"><i className="bi bi-person me-2"></i>Магический профиль</h5>
                  {isEditing ? (
                    <>
                      <div className="mb-3">
                        <label className="form-label text-moonlight">Имя</label>
                        <input
                          type="text"
                          className="form-control bg-dark-purple border-potion text-white"
                          value={profileData.name}
                          onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                          style={{ color: '#e6e6ff' }}
                        />
                      </div>
                      <div className="mb-3">
                        <label className="form-label text-moonlight">Email</label>
                        <input
                          type="email"
                          className="form-control bg-dark-purple border-potion text-white"
                          value={profileData.email}
                          onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                          style={{ color: '#e6e6ff' }}
                        />
                      </div>
                      <div className="mb-3">
                        <label className="form-label text-moonlight">Адрес доставки</label>
                        <input
                          type="text"
                          className="form-control bg-dark-purple border-potion text-white"
                          value={profileData.address}
                          onChange={(e) => setProfileData({ ...profileData, address: e.target.value })}
                          style={{ color: '#e6e6ff' }}
                        />
                      </div>
                      <div className="mb-3">
                        <label className="form-label text-moonlight">Биография</label>
                        <textarea
                          className="form-control bg-dark-purple border-potion text-white"
                          rows={3}
                          value={profileData.bio}
                          onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                          style={{ color: '#e6e6ff' }}
                        ></textarea>
                      </div>
                      <div className="d-flex gap-2">
                        <button type="button" className="btn btn-potion" onClick={handleSaveProfile}>
                          <i className="bi bi-check-circle me-1"></i>Сохранить
                        </button>
                        <button type="button" className="btn btn-outline-secondary" onClick={() => setIsEditing(false)}>
                          <i className="bi bi-x-circle me-1"></i>Отмена
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="row mb-3">
                        <div className="col-md-3"><strong className="text-moonlight">Имя:</strong></div>
                        <div className="col-md-9">{profileData.name}</div>
                      </div>
                      <div className="row mb-3">
                        <div className="col-md-3"><strong className="text-moonlight">Email:</strong></div>
                        <div className="col-md-9">{profileData.email}</div>
                      </div>
                      <div className="row mb-3">
                        <div className="col-md-3"><strong className="text-moonlight">Уровень:</strong></div>
                        <div className="col-md-9">{wizardInfo.desc}</div>
                      </div>
                      <div className="row mb-3">
                        <div className="col-md-3"><strong className="text-moonlight">Адрес:</strong></div>
                        <div className="col-md-9">{profileData.address || 'Не указан'}</div>
                      </div>
                      <div className="row mb-3">
                        <div className="col-md-3"><strong className="text-moonlight">Биография:</strong></div>
                        <div className="col-md-9">{profileData.bio || 'Нет данных'}</div>
                      </div>
                      <button type="button" className="btn btn-outline-potion" onClick={() => setIsEditing(true)}>
                        <i className="bi bi-pencil me-1"></i>Редактировать
                      </button>
                    </>
                  )}
                </div>
              )}

              {activeTab === 'security' && (
                <div>
                  <h5 className="text-potion mb-4"><i className="bi bi-shield-lock me-2"></i>Настройки безопасности</h5>
                  <div className="alert alert-info">
                    <div className="d-flex justify-content-between align-items-center">
                      <div>
                        <strong className="text-moonlight">2FA не настроена</strong>
                        <div className="text-muted small">Добавьте дополнительный уровень защиты</div>
                      </div>
                      <button className="btn btn-outline-potion btn-sm">
                        <i className="bi bi-shield-plus me-1"></i>Включить
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'notifications' && (
                <div>
                  <h5 className="text-potion mb-4"><i className="bi bi-bell me-2"></i>Уведомления</h5>
                  <div className="form-check form-switch mb-3">
                    <input className="form-check-input" type="checkbox" role="switch" id="allNotifications" defaultChecked />
                    <label className="form-check-label text-moonlight" htmlFor="allNotifications">Все уведомления</label>
                  </div>
                  <div className="form-check form-switch mb-3">
                    <input className="form-check-input" type="checkbox" role="switch" id="orderUpdates" defaultChecked />
                    <label className="form-check-label text-moonlight" htmlFor="orderUpdates">Статус заказа</label>
                  </div>
                  <div className="form-check form-switch">
                    <input className="form-check-input" type="checkbox" role="switch" id="promotions" />
                    <label className="form-check-label text-moonlight" htmlFor="promotions">Акции и скидки</label>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;