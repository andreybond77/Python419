import React from 'react';
import { StandardButtonProps } from '../types';

const StandardButton: React.FC<StandardButtonProps> = ({
  BGcolor,
  icon,
  title,
  btnType,
  onClick,
  className = '',
  disabled = false,
}) => {
  const baseClasses = `btn btn-${BGcolor} ${className}`.trim();

  return (
    <button
      type="button"
      className={baseClasses}
      onClick={onClick}
      title={title}
      disabled={disabled}
    >
      {btnType === 'iconButton' && icon ? (
        <i className={`bi bi-${icon}`}></i>
      ) : (
        title
      )}
    </button>
  );
};

export default StandardButton;