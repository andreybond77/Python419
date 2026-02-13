import React, { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

export const MainLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const { totalItems } = useCart();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      {/* Навигация */}
      <nav className="navbar navbar-expand-lg navbar-dark navbar-dark shadow-lg">
        <div className="container">
          <Link className="navbar-brand d-flex align-items-center" to="/" onClick={() => setIsMenuOpen(false)}>
            <div className="me-2">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor" className="text-potion">
                <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12C20,15.86 17.29,19.14 13.5,20.31L12,20.9L10.5,20.31C6.71,19.14 4,15.86 4,12A8,8 0 0,1 12,4Z" />
              </svg>
            </div>
            <span className="fw-bold fs-4 text-potion">Dark Moon Potions</span>
          </Link>
          <button
            className="navbar-toggler border-potion"
            type="button"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className={`collapse navbar-collapse ${isMenuOpen ? 'show' : ''}`}>
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/" onClick={() => setIsMenuOpen(false)}>
                  <i className="bi bi-house-door me-1"></i>Главная
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/potions" onClick={() => setIsMenuOpen(false)}>
                  <i className="bi bi-flask me-1"></i>Зелья
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/orders" onClick={() => setIsMenuOpen(false)}>
                  <i className="bi bi-bag-check me-1"></i>Заказы
                </Link>
              </li>
            </ul>
            <div className="d-flex align-items-center">
              <Link to="/cart" className="btn btn-outline-potion position-relative me-3" onClick={() => setIsMenuOpen(false)}>
                <i className="bi bi-cart me-1"></i>
                Корзина
                {totalItems > 0 && (
                  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                    {totalItems}
                  </span>
                )}
              </Link>
              {user ? (
                <div className="dropdown">
                  <button className="btn btn-outline-potion dropdown-toggle" type="button" id="navbarDropdown" data-bs-toggle="dropdown">
                    <i className="bi bi-person-circle me-1"></i>
                    {user.name}
                  </button>
                  <ul className="dropdown-menu dropdown-menu-end">
                    <li><Link className="dropdown-item" to="/profile" onClick={() => setIsMenuOpen(false)}>Профиль</Link></li>
                    <li><hr className="dropdown-divider" /></li>
                    <li><button className="dropdown-item text-danger" onClick={handleLogout}>Выйти</button></li>
                  </ul>
                </div>
              ) : (
                <div className="d-flex gap-2">
                  <Link to="/login" className="btn btn-outline-potion" onClick={() => setIsMenuOpen(false)}>Войти</Link>
                  <Link to="/register" className="btn btn-potion" onClick={() => setIsMenuOpen(false)}>Регистрация</Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Основной контент */}
      <main className="flex-grow-1 py-4">
        <div className="container">
          <Outlet />
        </div>
      </main>

      {/* Футер */}
      <footer className="bg-dark-purple py-4 mt-auto border-top border-potion">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-md-6">
              <div className="d-flex align-items-center">
                <div className="me-3">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="#9d4edd">
                    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12C20,15.86 17.29,19.14 13.5,20.31L12,20.9L10.5,20.31C6.71,19.14 4,15.86 4,12A8,8 0 0,1 12,4Z" />
                  </svg>
                </div>
                <div>
                  <h5 className="text-potion mb-1">Dark Moon Potions</h5>
                  <p className="mb-0 text-muted small">Магические зелья высшего качества</p>
                </div>
              </div>
            </div>
            <div className="col-md-6 text-md-end mt-3 mt-md-0">
              <div className="d-flex justify-content-md-end gap-3">
                <Link to="/about" className="text-muted text-decoration-none">О нас</Link>
                <Link to="/contact" className="text-muted text-decoration-none">Контакты</Link>
                <Link to="/support" className="text-muted text-decoration-none">Поддержка</Link>
              </div>
              <p className="text-muted small mb-0 mt-2">© 2024 Dark Moon Potions. Все права защищены.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};