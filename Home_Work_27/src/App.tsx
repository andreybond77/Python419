import React, { useState } from 'react';
import './App.css';
import ProductCard from './components/ProductCard';
import Modal from './components/Modal';
import Cart from './components/Cart';
import { rickAndMortyProducts, Product, CartItem } from './data';

const App: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState(''); // Новое состояние для поиска

  // Фильтрация товаров ТОЛЬКО по названию
  const filteredProducts = rickAndMortyProducts.filter(product => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return product.name.toLowerCase().includes(query);
  });

  // Логика добавления в корзину
  const handleAddToCart = (product: Product) => {
    setCartItems(prevItems => {
      const existingItem = prevItems.find(item => item.product.id === product.id);
      if (existingItem) {
        return prevItems.map(item =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevItems, { product, quantity: 1 }];
      }
    });
    console.log(`Товар "${product.name}" добавлен в корзину`);
  };

  // Логика открытия модального окна с деталями товара
  const handleViewDetails = (product: Product) => {
    setSelectedProduct(product);
    setIsModalOpen(true);
    console.log(`Открыты детали товара: ${product.name}`);
  };

  // Логика увеличения количества товара в корзине
  const handleIncrement = (product: Product) => {
    setCartItems(prevItems =>
      prevItems.map(item =>
        item.product.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      )
    );
    console.log(`Увеличено количество товара ${product.name}`);
  };

  // Логика уменьшения количества товара в корзине
  const handleDecrement = (product: Product) => {
    setCartItems(prevItems => {
      const existingItem = prevItems.find(item => item.product.id === product.id);
      if (existingItem && existingItem.quantity > 1) {
        return prevItems.map(item =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity - 1 }
            : item
        );
      } else {
        return prevItems.filter(item => item.product.id !== product.id);
      }
    });
    console.log(`Уменьшено количество товара ${product.name}`);
  };

  // Логика удаления товара из корзины
  const handleRemoveFromCart = (productId: number) => {
    setCartItems(prevItems => prevItems.filter(item => item.product.id !== productId));
    console.log(`Товар с ID ${productId} удален из корзины`);
  };

  // Логика оформления заказа
  const handleCheckout = () => {
    console.log('Заказ оформлен:', cartItems);
    alert('Заказ оформлен! Спасибо за покупку!');
    setCartItems([]);
    setIsCartOpen(false);
  };

  // Закрытие модального окна
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedProduct(null);
  };

  // Закрытие корзины
  const closeCart = () => {
    setIsCartOpen(false);
  };

  // Открытие корзины
  const openCart = () => {
    setIsCartOpen(true);
  };

  // Подсчет общего количества товаров в корзине
  const getTotalItems = () => {
    return cartItems.reduce((total, item) => total + item.quantity, 0);
  };

  return (
    <div className="container-fluid py-4">
      {/* Кнопка корзины в шапке */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="text-center flex-grow-1">Магазин Рик и Морти</h1>
        <button 
          className="btn btn-primary position-relative"
          onClick={openCart}
        >
          <i className="bi bi-cart-fill"></i> Корзина
          {getTotalItems() > 0 && (
            <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              {getTotalItems()}
            </span>
          )}
        </button>
      </div>

      {/* Поле ввода для поиска */}
      <div className="mb-4">
        <input
          type="text"
          className={`form-control mb-3 ${filteredProducts.length === 0 && searchQuery ? 'is-invalid' : ''}`}
          placeholder="Поиск товаров по названию..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {/* Сообщение "Ничего не найдено" */}
        {filteredProducts.length === 0 && searchQuery && (
          <p className="text-danger">
            <i className="bi bi-exclamation-circle"></i> Извините, по вашему запросу ничего не найдено
          </p>
        )}
      </div>

      {/* Сетка товаров */}
      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 g-4">
        {filteredProducts.map((product) => (
          <div className="col" key={product.id}>
            <ProductCard 
              product={product}
              onAddToCart={handleAddToCart}
              onViewDetails={handleViewDetails}
              onIncrement={handleIncrement}
              onDecrement={handleDecrement}
            />
          </div>
        ))}
      </div>

      {/* Модальное окно с деталями товара */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        product={selectedProduct}
        onAddToCart={handleAddToCart}
      />

      {/* Модальное окно корзины */}
      <Cart
        cartItems={cartItems}
        onIncrement={handleIncrement}
        onDecrement={handleDecrement}
        onRemove={handleRemoveFromCart}
        isOpen={isCartOpen}
        onClose={closeCart}
        onCheckout={handleCheckout}
      />
    </div>
  );
};

export default App;