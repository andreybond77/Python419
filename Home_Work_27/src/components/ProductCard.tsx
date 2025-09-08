import React from 'react';
import { ProductCardProps } from '../types';
import StandardButton from './StandardButton';

const ProductCard: React.FC<ProductCardProps> = ({ 
  product,
  onAddToCart,
  onViewDetails,
  onIncrement,
  onDecrement
}) => {
  return (
    <div className="card h-100 shadow-sm">
      <img 
        src={product.imageUrl} 
        className="card-img-top" 
        alt={product.name}
        style={{ height: '200px', objectFit: 'cover' }}
      />
      <div className="card-body d-flex flex-column">
        <h5 className="card-title">{product.name}</h5>
        <p className="card-text flex-grow-1">{product.description}</p>
        <p className="card-text">
          <strong>Цена: {product.price.toFixed(2)} шмеклей</strong>
        </p>
        <div className="d-flex flex-wrap gap-2 mt-auto">
          <StandardButton
            BGcolor="primary"
            icon="basket-fill"
            title="Добавить в корзину"
            btnType="iconButton"
            onClick={() => onAddToCart(product)}
          />
          <StandardButton
            BGcolor="info"
            icon="eye-fill"
            title="Посмотреть подробнее"
            btnType="iconButton"
            onClick={() => onViewDetails(product)}
          />
          <StandardButton
            BGcolor="success"
            icon="plus-lg"
            title="Увеличить"
            btnType="iconButton"
            onClick={() => onIncrement(product)}
          />
          <StandardButton
            BGcolor="warning"
            icon="dash-lg"
            title="Уменьшить"
            btnType="iconButton"
            onClick={() => onDecrement(product)}
          />
        </div>
      </div>
    </div>
  );
};

export default ProductCard;