import React from 'react';
import { ModalProps } from '../types';
import StandardButton from './StandardButton';

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, product, onAddToCart }) => {
  if (!isOpen || !product) return null;

  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(product);
    }
    onClose();
  };

  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }} onClick={onClose}>
      <div className="modal-dialog modal-lg" onClick={e => e.stopPropagation()}>
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{product.name}</h5>
            <StandardButton
              BGcolor="secondary"
              icon="x-lg"
              title="Закрыть"
              btnType="iconButton"
              onClick={onClose}
              className="btn-close"
            />
          </div>
          <div className="modal-body">
            <div className="row">
              <div className="col-md-6">
                <img 
                  src={product.imageUrl} 
                  className="img-fluid rounded" 
                  alt={product.name}
                  style={{ height: '300px', objectFit: 'cover' }}
                />
              </div>
              <div className="col-md-6">
                <p className="lead">{product.description}</p>
                <h4 className="text-primary">Цена: {product.price.toFixed(2)} шмеклей</h4>
                <div className="mt-3">
                  <StandardButton
                    BGcolor="primary"
                    icon="basket-fill"
                    title="Добавить в корзину"
                    btnType="textButton"
                    onClick={handleAddToCart}
                    className="w-100"
                  />
                </div>
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <StandardButton
              BGcolor="secondary"
              title="Закрыть"
              btnType="textButton"
              onClick={onClose}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;