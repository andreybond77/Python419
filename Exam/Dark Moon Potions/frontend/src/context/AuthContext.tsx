import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUser = () => {
      try {
        const storedUser = localStorage.getItem('darkMoonUser');
        if (storedUser) {
          const parsedUser = JSON.parse(storedUser);
          // Проверяем, что все обязательные поля пользователя существуют
          if (parsedUser && parsedUser.id && parsedUser.email) {
            setUser(parsedUser);
          } else {
            console.warn("Некорректные данные пользователя в localStorage");
            localStorage.removeItem('darkMoonUser');
          }
        }
      } catch (e) {
        console.error("Ошибка загрузки пользователя из localStorage:", e);
        localStorage.removeItem('darkMoonUser');
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Тестовые учетные данные
      if (email === 'test@example.com' && password === 'password') {
        const mockUser: User = {
          id: 1,
          email: email,
          name: email.split('@')[0],
          wizardLevel: 'apprentice',
          is_active: true,
          is_verified: true,
          address: 'Лесная тропа, 7, Хогсмид',
          bio: 'Изучаю магию и создание зелий.',
          preferences: {
            favoriteCategory: 'healing',
            newsletter: true,
            promotions: false
          }
        };
        setUser(mockUser);
        localStorage.setItem('darkMoonUser', JSON.stringify(mockUser));
      } else {
        throw new Error('Неверный email или пароль');
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Проверка email
      if (!email.includes('@')) {
        throw new Error('Некорректный email');
      }

      const mockNewUser: User = {
        id: Date.now(),
        email: email,
        name: email.split('@')[0],
        wizardLevel: 'novice',
        is_active: true,
        is_verified: false,
        address: '',
        bio: '',
        preferences: {
          favoriteCategory: 'physical',
          newsletter: true,
          promotions: true
        }
      };
      setUser(mockNewUser);
      localStorage.setItem('darkMoonUser', JSON.stringify(mockNewUser));
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    try {
      localStorage.removeItem('darkMoonUser');
    } catch (e) {
      console.error("Ошибка при выходе:", e);
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    isLoading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};