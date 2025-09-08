export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
}

// Тип для цветов Bootstrap
export type BSColors = "primary" | "success" | "warning" | "danger" | "info" | "secondary" | "dark" | "light";

// Интерфейс для пропсов кнопки
export interface StandardButtonProps {
  BGcolor: BSColors;
  icon?: string;
  title: string;
  btnType: "textButton" | "iconButton";
  onClick: () => void;
  className?: string;
  disabled?: boolean;
}

// Интерфейс для пропсов карточки товара
export interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  onViewDetails: (product: Product) => void;
  onIncrement: (product: Product) => void;
  onDecrement: (product: Product) => void;
}

// Интерфейс для элемента корзины
export interface CartItem {
  product: Product;
  quantity: number;
}

// Интерфейс для модального окна
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product | null;
  onAddToCart?: (product: Product) => void;
}