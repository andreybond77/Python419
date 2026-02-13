# backend/seed_data.py
import asyncio
import sys
import os
import json
import uuid
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import AsyncSessionLocal
from models.user import User
from models.potion import Potion, PotionCategory
from models.cart import Cart, CartItem
from models.order import Order, OrderItem, OrderStatus
from models.review import Review
from models.wishlist import Wishlist
from models.payment import Payment
from services.user_service import UserService

user_service = UserService()

# Данные из вашего файла seed_data.py (я возьму несколько примеров)
POTIONS_DATA = [
    {
        "id": 1,
        "name": "Зелье Лунного Сияния",
        "slug": "zelie-lunnogo-siyaniya",
        "description": "Физическое зелье, дающее силу и выносливость под светом луны. Усиливает физические способности в три раза.",
        "price": 1299.99,
        "image_url": "/images/potion_1.webp",
        "category": "physical",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "3 лунных цикла",
        "brewing_difficulty": "medium",
        "ingredients": ["Лунный камень", "Серебряная роса", "Корень мандрагоры"],
        "effects": ["+300% сила", "+250% выносливость", "Ночное зрение"],
        "warnings": ["Не смешивать с солнечными зельями", "Только для взрослых волшебников"]
    },
    {
        "id": 2,
        "name": "Эликсир Ясного Ума",
        "slug": "eliksir-yasnogo-uma",
        "description": "Психическое зелье для улучшения концентрации и памяти. Используется магами перед важными ритуалами.",
        "price": 899.99,
        "image_url": "/images/potion_2.webp",
        "category": "mental",
        "rarity": "rare",
        "in_stock": True,
        "brewing_time": "7 дней",
        "brewing_difficulty": "easy",
        "ingredients": ["Цветок лотоса", "Пыльца фей", "Кристалл кварца"],
        "effects": ["Улучшенная память", "Повышенная концентрация", "Защита от ментальных атак"],
        "warnings": ["Максимум 1 доза в неделю", "Избегать при психических расстройствах"]
    },
    {
        "id": 3,
        "name": "Бальзам Феникса",
        "slug": "balzam-feniksa",
        "description": "Целительное зелье высшего качества. Заживляет любые раны и восстанавливает жизненную энергию.",
        "price": 2499.99,
        "image_url": "/images/potion_10.webp",
        "category": "healing",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "40 дней и ночей",
        "brewing_difficulty": "hard",
        "ingredients": ["Слеза феникса", "Золотой корень", "Святая вода"],
        "effects": ["Полное заживление ран", "Восстановление энергии", "Очищение от ядов"],
        "warnings": ["Очень редкие ингредиенты", "Только для экстренных случаев"]
    },
    {
        "id": 4,
        "name": "Оборотное Зелье",
        "slug": "oborotnoe-zelie",
        "description": "Преображающее зелье для принятия облика другого человека на ограниченное время.",
        "price": 3299.99,
        "image_url": "/images/potion_5.webp",
        "category": "transformative",
        "rarity": "legendary",
        "in_stock": False,
        "brewing_time": "Полнолуние + 13 дней",
        "brewing_difficulty": "hard",
        "ingredients": ["Волос цели", "Кость двойника", "Зеркальная вода"],
        "effects": ["Полная трансформация", "Голос цели", "Временные воспоминания"],
        "warnings": ["Не более 1 часа", "Требуется разрешение Министерства"]
    },
    {
        "id": 5,
        "name": "Щитовая Настойка",
        "slug": "shitovaya-nastoika",
        "description": "Защитное зелье, создающее магический щит, снижающий урон от заклинаний и физических атак.",
        "price": 1599.99,
        "image_url": "/images/potion_3.webp",
        "category": "protective",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "14 дней",
        "brewing_difficulty": "medium",
        "ingredients": ["Порошок драконьей чешуи", "Смола щитового дерева", "Масло вампира"],
        "effects": ["Снижение урона на 50%", "Сопротивление магии", "Блокировка заклинаний"],
        "warnings": ["Не совмещать с боевыми зельями", "Возможна аллергия на вампирье масла"]
    },
    {
        "id": 6,
        "name": "Зелье Пламенного Гнева",
        "slug": "zelie-plamennogo-gneva",
        "description": "Боевое зелье, наделяющее волшебника способностью выпускать магический огонь и проклинать врагов.",
        "price": 1899.99,
        "image_url": "/images/potion_24.webp",
        "category": "combat",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "21 день",
        "brewing_difficulty": "hard",
        "ingredients": ["Пеплофеникса", "Серный кристалл", "Кровь саламандры"],
        "effects": ["Магический огонь", "Проклятие пламени", "Площадь поражения 10м"],
        "warnings": ["Опасное оружие", "Требуется лицензия", "Не для новичков"]
    },
    {
        "id": 7,
        "name": "Ночная Тень",
        "slug": "nochnaya-ten",
        "description": "Смертельный яд без запаха и вкуса. Действует через 24 часа после приема.",
        "price": 4999.99,
        "image_url": "/images/potion_32.webp",
        "category": "poison",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "Полнолуние + новолуние",
        "brewing_difficulty": "expert",
        "ingredients": ["Прах вампира", "Капля крови лича", "Лунная вода"],
        "effects": ["Смертельное действие", "Невидимость токсинов", "Мгновенная реакция"],
        "warnings": ["Исключительно для темных магов", "Не подлежит продаже новичкам"]
    },
    {
        "id": 8,
        "name": "Зелье Молодости",
        "slug": "zelie-molodosti",
        "description": "Преображающее зелье, возвращающее молодость и обновляющее клетки организма.",
        "price": 4599.99,
        "image_url": "/images/potion_30.webp",
        "category": "transformative",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "99 дней",
        "brewing_difficulty": "expert",
        "ingredients": ["Эссенция времени", "Слеза единорога", "Корень вечной жизни"],
        "effects": ["Омоложение на 20 лет", "Улучшение кожи", "Укрепление тела"],
        "warnings": ["Один раз в 100 лет", "Не для несовершеннолетних волшебников"]
    },
    {
        "id": 9,
        "name": "Любовный Напиток",
        "slug": "lyubovnyi-napitok",
        "description": "Психическое зелье, вызывающее сильное чувство влечения к человеку, который его дал.",
        "price": 749.99,
        "image_url": "/images/potion_31.webp",
        "category": "mental",
        "rarity": "rare",
        "in_stock": True,
        "brewing_time": "3 дня",
        "brewing_difficulty": "easy",
        "ingredients": ["Петалли розы", "Сердце пегаса", "Поцелуй нимфы"],
        "effects": ["Сильное влечение", "Чувство эйфории", "Потеря интереса к другим"],
        "warnings": ["Использовать с осторожностью", "Необратимо без заклинания снятия"]
    },
    {
        "id": 10,
        "name": "Антитоксин Святого Нарвала",
        "slug": "antitoksin-svyatogo-narvala",
        "description": "Целительное зелье, нейтрализующее большинство известных ядов и проклятий.",
        "price": 1799.99,
        "image_url": "/images/potion_19.webp",
        "category": "healing",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "33 дня",
        "brewing_difficulty": "medium",
        "ingredients": ["Рог нарвала", "Слеза ангела", "Корень жизни"],
        "effects": ["Нейтрализация ядов", "Снятие проклятий", "Очищение крови"],
        "warnings": ["Не эффективен против Ночной Тени", "Только для сертифицированных целителей"]
    },
    {
        "id": 11,
        "name": "Зелье Летучей Мыши",
        "slug": "zelie-letuchei-myshi",
        "description": "Физическое зелье, позволяющее видеть в полной темноте и летать на небольшие расстояния.",
        "price": 899.99,
        "image_url": "/images/potion_20.webp",
        "category": "physical",
        "rarity": "rare",
        "in_stock": True,
        "brewing_time": "7 лунных ночей",
        "brewing_difficulty": "easy",
        "ingredients": ["Крыло летучей мыши", "Сок ночной орхидеи", "Пыльца летучего дракона"],
        "effects": ["Ночное зрение", "Кратковременный полет", "Улучшенный слух"],
        "warnings": ["Действует 3 часа", "Не пить перед сном"]
    },
    {
        "id": 12,
        "name": "Эликсир Забытия",
        "slug": "eliksir-zabytiya",
        "description": "Психическое зелье, стирающее определенные воспоминания на выбор.",
        "price": 2199.99,
        "image_url": "/images/potion_16.webp",
        "category": "mental",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "13 дней",
        "brewing_difficulty": "hard",
        "ingredients": ["Память феникса", "Песок времени", "Цветок забвения"],
        "effects": ["Выборочное стирание памяти", "Снятие травм", "Очищение разума"],
        "warnings": ["Необратимый эффект", "Требуется разрешение Совета Магов"]
    },
    {
        "id": 13,
        "name": "Бальзам Драконьей Кожи",
        "slug": "balzam-drakonei-kozhi",
        "description": "Целительное зелье для мгновенного заживления ожогов и защиты от огня.",
        "price": 1599.99,
        "image_url": "/images/potion_12.webp",
        "category": "healing",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "28 дней",
        "brewing_difficulty": "medium",
        "ingredients": ["Чешуя дракона", "Пламя саламандры", "Корень огнецвета"],
        "effects": ["Заживление ожогов", "Защита от огня", "Укрепление кожи"],
        "warnings": ["Временный эффект", "Не для внутреннего применения"]
    },
    {
        "id": 14,
        "name": "Зелье Невидимости",
        "slug": "zelie-nevidimosti",
        "description": "Преображающее зелье, делающее волшебника невидимым для глаз и магических детекторов.",
        "price": 3899.99,
        "image_url": "/images/potion_9.webp",
        "category": "transformative",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "Полнолуние",
        "brewing_difficulty": "expert",
        "ingredients": ["Слеза хамелеона", "Тень призрака", "Воздух пустоты"],
        "effects": ["Полная невидимость", "Скрытие от магии", "Тихие шаги"],
        "warnings": ["Действует 1 час", "Запрещено в городах"]
    },
    {
        "id": 15,
        "name": "Настойка Каменной Кожи",
        "slug": "nastoika-kamennoi-kozhi",
        "description": "Защитное зелье, превращающее кожу в камень на ограниченное время.",
        "price": 2299.99,
        "image_url": "/images/potion_23.webp",
        "category": "protective",
        "rarity": "epic",
        "in_stock": False,
        "brewing_time": "21 день",
        "brewing_difficulty": "medium",
        "ingredients": ["Порошок гранита", "Кровь голема", "Камень горного тролля"],
        "effects": ["Кожа как камень", "Иммунитет к физических атакам", "Защита от стрел"],
        "warnings": ["Замедление движения", "Нельзя использовать дольше 30 минут"]
    },
    {
        "id": 16,
        "name": "Эликсир Ледяного Дыхания",
        "slug": "eliksir-ledyanogo-dyhaniya",
        "description": "Боевое зелье, позволяющее замораживать врагов и создавать ледяные преграды.",
        "price": 1799.99,
        "image_url": "/images/potion_8.webp",
        "category": "combat",
        "rarity": "rare",
        "in_stock": True,
        "brewing_time": "14 дней зимой",
        "brewing_difficulty": "medium",
        "ingredients": ["Ледяной кристалл", "Дыхание белого дракона", "Снег с вершины горы"],
        "effects": ["Ледяное дыхание", "Создание ледяных стен", "Замедление врагов"],
        "warnings": ["Риск обморожения", "Только для опытных магов"]
    },
    {
        "id": 17,
        "name": "Яд Паутины",
        "slug": "yad-pautiny",
        "description": "Медленно действующий яд, парализующий жертву и превращающий ее в куколку.",
        "price": 3499.99,
        "image_url": "/images/potion_11.webp",
        "category": "poison",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "Лунное затмение",
        "brewing_difficulty": "hard",
        "ingredients": ["Яд черной вдовы", "Паутина арахнида", "Нектар смертоцвета"],
        "effects": ["Паралич", "Превращение в куколку", "Медленная смерть"],
        "warnings": ["Смертельно опасно", "Запрещено в 200 странах"]
    },
    {
        "id": 18,
        "name": "Зелье Звериного Облика",
        "slug": "zelie-zverinogo-oblika",
        "description": "Преображающее зелье для превращения в любое животное на выбор.",
        "price": 2899.99,
        "image_url": "/images/potion_22.webp",
        "category": "transformative",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "7 дней по выбору животного",
        "brewing_difficulty": "hard",
        "ingredients": ["Шерсть нужного зверя", "Коготь хищника", "Сердце шамана"],
        "effects": ["Превращение в животное", "Сохраняется разум", "Усиленные чувства зверя"],
        "warnings": ["Риск остаться в облике", "Требуется практика"]
    },
    {
        "id": 19,
        "name": "Эликсир Ясновидения",
        "slug": "eliksir-yasnovideniya",
        "description": "Психическое зелье для предсказания будущего и видения скрытых вещей.",
        "price": 3199.99,
        "image_url": "/images/potion_18.webp",
        "category": "mental",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "Новолуние + 7 дней",
        "brewing_difficulty": "expert",
        "ingredients": ["Глаз провидца", "Зеркало будущего", "Туман времени"],
        "effects": ["Видение будущего", "Обнаружение скрытого", "Чтение мыслей"],
        "warnings": ["Может показать ужасное", "Только для сильных разумом"]
    },
    {
        "id": 20,
        "name": "Бальзам Регенерации",
        "slug": "balzam-regeneratsii",
        "description": "Целительное зелье для восстановления утраченных конечностей и органов.",
        "price": 5999.99,
        "image_url": "/images/potion_15.webp",
        "category": "healing",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "40 дней и 40 ночей",
        "brewing_difficulty": "expert",
        "ingredients": ["Кровь гидры", "Клетки саламандры", "Корень бессмертия"],
        "effects": ["Регенерация конечностей", "Восстановление органов", "Омоложение клеток"],
        "warnings": ["Сильная боль при применении", "Одноразовое использование"]
    },
    {
        "id": 21,
        "name": "Зелье Исполинской Силы",
        "slug": "zelie-ispolinskoi-sily",
        "description": "Физическое зелье, временно увеличивающее рост и силу в 10 раз.",
        "price": 2499.99,
        "image_url": "/images/potion_27.webp",
        "category": "physical",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "Полнолуние + 3 дня",
        "brewing_difficulty": "medium",
        "ingredients": ["Кость гиганта", "Мышцы тролля", "Сердце титана"],
        "effects": ["Рост до 5 метров", "Сила 10 человек", "Неуязвимость к ударам"],
        "warnings": ["Эффект 30 минут", "Сильная усталость после"]
    },
    {
        "id": 22,
        "name": "Эликсир Мертвого Сна",
        "slug": "eliksir-mertvogo-sna",
        "description": "Психическое зелье, погружающее в глубокий сон, неотличимый от смерти.",
        "price": 1699.99,
        "image_url": "/images/potion_26.webp",
        "category": "mental",
        "rarity": "rare",
        "in_stock": True,
        "brewing_time": "13 ночей",
        "brewing_difficulty": "medium",
        "ingredients": ["Лепесток сонного мака", "Пыльца дремоты", "Слеза спящей красавицы"],
        "effects": ["Глубокий сон", "Замедление метаболизма", "Восстановление психики"],
        "warnings": ["Риск вечного сна", "Только под наблюдением"]
    },
    {
        "id": 23,
        "name": "Целебный Нектар",
        "slug": "tselebnyi-nektar",
        "description": "Целительное зелье для лечения магических болезней и снятия проклятий.",
        "price": 1899.99,
        "image_url": "/images/potion_13.webp",
        "category": "healing",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "21 день весной",
        "brewing_difficulty": "medium",
        "ingredients": ["Нектар цветка жизни", "Роса бессмертия", "Сок священного дерева"],
        "effects": ["Лечение магических болезней", "Снятие слабых проклятий", "Очищение ауры"],
        "warnings": ["Неэффективно против темной магии", "Только для светлых магов"]
    },
    {
        "id": 24,
        "name": "Зелье Подводного Дыхания",
        "slug": "zelie-podvodnogo-dyhaniya",
        "description": "Преображающее зелье для дыхания под водой и жизни в океане.",
        "price": 1399.99,
        "image_url": "/images/potion_14.webp",
        "category": "transformative",
        "rarity": "rare",
        "in_stock": True,
        "brewing_time": "Прилив + отлив",
        "brewing_difficulty": "easy",
        "ingredients": ["Жабры русалки", "Чешуя тритона", "Водоросли глубин"],
        "effects": ["Дыхание под водой", "Защита от давления", "Общение с морскими существами"],
        "warnings": ["Действует 24 часа", "Риск остаться с жабрами"]
    },
    {
        "id": 25,
        "name": "Амулетная Настойка",
        "slug": "amuletnaya-nastoika",
        "description": "Защитное зелье для создания персонального магического щита вокруг владельца.",
        "price": 2799.99,
        "image_url": "/images/potion_6.webp",
        "category": "protective",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "33 дня в замке",
        "brewing_difficulty": "hard",
        "ingredients": ["Пыль амулета", "Сердцевина щита", "Эссенция защиты"],
        "effects": ["Персональный щит", "Отражение заклинаний", "Защита от проклятий"],
        "warnings": ["Действует 7 дней", "Требуется перезарядка"]
    },
    {
        "id": 26,
        "name": "Громовой Эликсир",
        "slug": "gromovoi-eliksir",
        "description": "Боевое зелье для призыва молний и управления погодой.",
        "price": 3299.99,
        "image_url": "/images/potion_27.webp",
        "category": "combat",
        "rarity": "legendary",
        "in_stock": False,
        "brewing_time": "Гроза + 7 дней",
        "brewing_difficulty": "expert",
        "ingredients": ["Молния Зевса", "Громовой камень", "Облачная вата"],
        "effects": ["Призыв молний", "Управление грозой", "Электрические разряды"],
        "warnings": ["Опасность для окружающих", "Только на открытой местности"]
    },
    {
        "id": 27,
        "name": "Яд Безумия",
        "slug": "yad-bezumiya",
        "description": "Психический яд, вызывающий галлюцинации и потерю рассудка.",
        "price": 4199.99,
        "image_url": "/images/potion_25.webp",
        "category": "poison",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "Безумная луна",
        "brewing_difficulty": "hard",
        "ingredients": ["Мозг сумасшедшего", "Гриб галлюциноген", "Слеза демона"],
        "effects": ["Сильные галлюцинации", "Потера памяти", "Безумие"],
        "warnings": ["Необратимые повреждения психики", "Запрещен во всех цивилизованных странах"]
    },
    {
        "id": 28,
        "name": "Эликсир Правды",
        "slug": "eliksir-pravdy",
        "description": "Психическое зелье, заставляющее говорить только правду.",
        "price": 1199.99,
        "image_url": "/images/potion_28.webp",
        "category": "mental",
        "rarity": "rare",
        "in_stock": True,
        "brewing_time": "Солнцестояние",
        "brewing_difficulty": "easy",
        "ingredients": ["Язык правдивца", "Сердце честного", "Корень откровения"],
        "effects": ["Принуждение к правде", "Раскрытие тайн", "Честность"],
        "warnings": ["Действует 1 час", "Может раскрыть ваши секреты"]
    },
    {
        "id": 29,
        "name": "Зелье Кошачьей Грации",
        "slug": "zelie-koshachei-gratsii",
        "description": "Физическое зелье для обретения ловкости, гибкости и бесшумности кошки.",
        "price": 999.99,
        "image_url": "/images/potion_7.webp",
        "category": "physical",
        "rarity": "common",
        "in_stock": True,
        "brewing_time": "3 дня",
        "brewing_difficulty": "easy",
        "ingredients": ["Усы кота", "Когти пантеры", "Молоко черной кошки"],
        "effects": ["Кошачья ловкость", "Бесшумное движение", "Падение с высоты без урона"],
        "warnings": ["Желание играть с клубками", "Неприязнь к воде"]
    },
    {
        "id": 30,
        "name": "Последнее Прибежище",
        "slug": "poslednee-pribezhishche",
        "description": "Легендарное целительное зелье, спасающее от любой болезни, раны или проклятия.",
        "price": 9999.99,
        "image_url": "/images/potion_21.webp",
        "category": "healing",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "100 лет и 1 день",
        "brewing_difficulty": "expert",
        "ingredients": ["Слеза богини", "Кровь феникса", "Пыльца рая", "Корень мироздания"],
        "effects": ["Полное исцеление", "Воскрешение (в течение часа)", "Бессмертие на 1 год"],
        "warnings": ["Одна на весь мир в столетие", "Цена - половина души"]
    },
    {
        "id": 31,
        "name": "Эликсир Вечного Голода",
        "slug": "eliksir-vechnogo-goloda",
        "description": "Физическое зелье, многократно ускоряющее метаболизм и позволяющее поглощать магическую энергию из любой пищи.",
        "price": 1899.99,
        "image_url": "/images/potion_29.webp",
        "category": "physical",
        "rarity": "epic",
        "in_stock": True,
        "brewing_time": "Полнолуние в убывающей фазе",
        "brewing_difficulty": "medium",
        "ingredients": ["Желудок обжоры", "Слюна голодного демона", "Корень ненасытности", "Пепсид вечно голодного"],
        "effects": ["Поглощение магии из пищи", "Ускоренный метаболизм x10", "Невосприимчивость к ядам в еде", "Энергия от любой органики"],
        "warnings": ["Постоянный голод", "Риск ожирения при обычной пище", "Требует специальной диеты", "Зависимость от зелья"]
    },
    {
        "id": 32,
        "name": "Зелье Хранителя Времени",
        "slug": "zelie-hranitelya-vremeni",
        "description": "Психическое зелье, позволяющее на 5 минут замедлить время вокруг себя до 1% от нормальной скорости.",
        "price": 7499.99,
        "image_url": "/images/potion_17.webp",
        "category": "mental",
        "rarity": "legendary",
        "in_stock": True,
        "brewing_time": "Солнечное затмение + лунное затмение",
        "brewing_difficulty": "expert",
        "ingredients": ["Песчинка из часов Судного дня", "Слеза Хроноса", "Кристалл замерзшего времени", "Перо птицы, видевшей начало мира"],
        "effects": ["Замедление времени до 1%", "Ускоренное восприятие", "Возможность видеть пульсацию времени", "Краткий взгляд в прошлое и будущее"],
        "warnings": ["Старение на 1 день за каждую минуту использования", "Риск застрять во временной петле", "Запрещено Хранителями Времени", "Может привлечь внимание временных парадоксов"]
    }
]

CATEGORIES_DATA = [
    {
        "name": "Физические",
        "slug": "physical",
        "description": "Зелья для усиления физических способностей",
        "icon": "💪",
        "color": "#ff6b6b"
    },
    {
        "name": "Психические", 
        "slug": "mental",
        "description": "Зелья для улучшения ментальных способностей",
        "icon": "🧠",
        "color": "#4d96ff"
    },
    {
        "name": "Целительные",
        "slug": "healing",
        "description": "Зелья для лечения и восстановления",
        "icon": "❤️",
        "color": "#6bcf7f"
    },
    {
        "name": "Преобразующие",
        "slug": "transformative",
        "description": "Зелья для изменения формы и облика",
        "icon": "🌀",
        "color": "#9d4edd"
    },
    {
        "name": "Защитные",
        "slug": "protective",
        "description": "Зелья для создания защитных барьеров",
        "icon": "🛡️",
        "color": "#ffa94d"
    },
    {
        "name": "Боевые",
        "slug": "combat",
        "description": "Зелья для боевых и наступательных целей",
        "icon": "⚔️",
        "color": "#ff4d4d"
    },
    {
        "name": "Яды",
        "slug": "poison",
        "description": "Смертельные и парализующие зелья",
        "icon": "☠️",
        "color": "#333333"
    }
]

async def seed_database():
    """Заполняет базу данных тестовыми данными."""
    print("🌙 Начинаю заполнение базы данных Dark Moon Potions...")
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. СОЗДАЕМ КАТЕГОРИИ
            print("1. Создание категорий зелий...")
            categories_map = {}
            
            for cat_data in CATEGORIES_DATA:
                category = PotionCategory(
                    id=str(uuid.uuid4()),
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    icon=cat_data.get("icon"),
                    color=cat_data.get("color")
                )
                session.add(category)
                categories_map[cat_data["slug"]] = category
            
            await session.flush()
            print(f"   ✅ Создано {len(categories_map)} категорий")
            
            # 2. СОЗДАЕМ ЗЕЛЬЯ
            print("2. Создание зелий...")
            potions_map = {}
            
            for potion_data in POTIONS_DATA:
                # Находим категорию
                category_slug = potion_data["category"]
                category = categories_map.get(category_slug)
                
                if not category:
                    print(f"   ⚠️  Категория '{category_slug}' не найдена для зелья '{potion_data['name']}'")
                    continue
                
                # Создаем зелье
                potion = Potion(
                    id=str(uuid.uuid4()),
                    name=potion_data["name"],
                    slug=potion_data["slug"],
                    description=potion_data["description"],
                    category_id=category.id,
                    category=category.name,
                    price=potion_data["price"],
                    original_price=potion_data.get("original_price", potion_data["price"] * 1.2 if potion_data.get("discount_percent") else None),
                    discount_percent=potion_data.get("discount_percent", 0),
                    in_stock=potion_data.get("in_stock", True),
                    stock_quantity=potion_data.get("stock_quantity", 10),
                    min_stock_level=5,
                    rarity=potion_data["rarity"],
                    brewing_time=potion_data["brewing_time"],
                    brewing_difficulty=potion_data["brewing_difficulty"],
                    image_url=potion_data["image_url"],
                    thumbnail_url=potion_data.get("thumbnail_url"),
                    popularity_score=potion_data.get("popularity_score", 50),
                    purchase_count=0,
                    review_count=0,
                    average_rating=0.0
                )
                
                # Устанавливаем списки через свойства
                potion.ingredients = potion_data.get("ingredients", [])
                potion.effects = potion_data.get("effects", [])
                potion.warnings = potion_data.get("warnings", [])
                potion.image_gallery = potion_data.get("image_gallery", [potion_data["image_url"]])
                
                session.add(potion)
                potions_map[potion.slug] = potion
            
            await session.flush()
            print(f"   ✅ Создано {len(potions_map)} зелий")
            
            # 3. СОЗДАЕМ ТЕСТОВОГО ПОЛЬЗОВАТЕЛЯ
            print("3. Создание тестовых пользователей...")
            
            # Администратор
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@darkmoon.com",
                username="admin",
                hashed_password=user_service.get_password_hash("admin123"),
                full_name="Администратор Системы",
                wizard_level="archmage",
                is_active=True,
                is_verified=True,
                is_staff=True,
                is_superuser=True,
                avatar_url="/images/admin_avatar.jpg"
            )
            session.add(admin_user)
            
            # Обычный пользователь
            test_user = User(
                id=str(uuid.uuid4()),
                email="user@example.com",
                username="testuser",
                hashed_password=user_service.get_password_hash("password123"),
                full_name="Тестовый Пользователь",
                wizard_level="adept",
                is_active=True,
                is_verified=True,
                preferences={"favoriteCategory": "healing", "newsletter": True}
            )
            session.add(test_user)
            
            await session.flush()
            print("   ✅ Создано 2 пользователя (admin и testuser)")
            
            # 4. СОЗДАЕМ КОРЗИНЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
            print("4. Создание корзин...")
            
            admin_cart = Cart(
                id=str(uuid.uuid4()),
                user_id=admin_user.id,
                total_items=0,
                total_price=0.0
            )
            session.add(admin_cart)
            
            test_cart = Cart(
                id=str(uuid.uuid4()),
                user_id=test_user.id,
                total_items=0,
                total_price=0.0
            )
            session.add(test_cart)
            
            # 5. ДОБАВЛЯЕМ ЗЕЛЬЯ В КОРЗИНУ ТЕСТОВОГО ПОЛЬЗОВАТЕЛЯ
            print("5. Добавление зелий в корзину...")
            
            # Добавляем первые 2 зелья в корзину
            potion_list = list(potions_map.values())
            if len(potion_list) >= 2:
                cart_items = [
                    CartItem(
                        id=str(uuid.uuid4()),
                        cart_id=test_cart.id,
                        potion_id=potion_list[0].id,
                        quantity=1,
                        price_per_unit=potion_list[0].price,
                        potion_name=potion_list[0].name,
                        potion_image=potion_list[0].image_url,
                        potion_category=potion_list[0].category
                    ),
                    CartItem(
                        id=str(uuid.uuid4()),
                        cart_id=test_cart.id,
                        potion_id=potion_list[1].id,
                        quantity=2,
                        price_per_unit=potion_list[1].price,
                        potion_name=potion_list[1].name,
                        potion_image=potion_list[1].image_url,
                        potion_category=potion_list[1].category
                    )
                ]
                session.add_all(cart_items)
                
                # Обновляем итоги корзины
                test_cart.total_items = 3
                test_cart.total_price = (
                    potion_list[0].price * 1 + 
                    potion_list[1].price * 2
                )
                
                print(f"   ✅ Добавлено {len(cart_items)} зелий в корзину")
            
            # 6. СОЗДАЕМ ОТЗЫВЫ
            print("6. Создание отзывов...")
            
            if potion_list:
                reviews = [
                    Review(
                        id=str(uuid.uuid4()),
                        user_id=test_user.id,
                        potion_id=potion_list[0].id,
                        rating=5,
                        title="Отличное зелье!",
                        comment="Действительно усиливает физические способности. Очень доволен покупкой!",
                        is_approved=True,
                        is_verified_purchase=True,
                        helpful_count=12,
                        not_helpful_count=1
                    ),
                    Review(
                        id=str(uuid.uuid4()),
                        user_id=test_user.id,
                        potion_id=potion_list[1].id,
                        rating=4,
                        title="Хорошо для концентрации",
                        comment="Помогает сосредоточиться перед сложными ритуалами. Минус - действует недолго.",
                        is_approved=True,
                        is_verified_purchase=True,
                        helpful_count=8
                    )
                ]
                session.add_all(reviews)
                
                # Обновляем статистику зелий
                potion_list[0].review_count = 1
                potion_list[0].average_rating = 5.0
                potion_list[1].review_count = 1
                potion_list[1].average_rating = 4.0
                
                print(f"   ✅ Создано {len(reviews)} отзыва")
            
            # 7. СОЗДАЕМ СПИСОК ЖЕЛАНИЙ
            print("7. Создание списка желаний...")
            
            if len(potion_list) >= 3:
                wishlist_items = [
                    Wishlist(
                        id=str(uuid.uuid4()),
                        user_id=test_user.id,
                        potion_id=potion_list[2].id,
                        note="Хочу купить на день рождения"
                    ),
                    Wishlist(
                        id=str(uuid.uuid4()),
                        user_id=test_user.id,
                        potion_id=potion_list[3].id if len(potion_list) >= 4 else potion_list[0].id,
                        note="Интересное зелье для исследований"
                    )
                ]
                session.add_all(wishlist_items)
                print(f"   ✅ Создано {len(wishlist_items)} элемента в списке желаний")
            
            # 8. СОХРАНЯЕМ ВСЕ ИЗМЕНЕНИЯ
            print("8. Сохранение данных...")
            await session.commit()
            
            print("\n" + "="*60)
            print("✅ БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!")
            print("="*60)
            print("\nТЕСТОВЫЕ ДАННЫЕ:")
            print("-" * 40)
            print("👑 АДМИНИСТРАТОР:")
            print(f"  Логин: admin@darkmoon.com")
            print(f"  Пароль: admin123")
            print(f"  Уровень: Администратор (все права)")
            print()
            print("👤 ПОЛЬЗОВАТЕЛЬ:")
            print(f"  Логин: user@example.com")
            print(f"  Пароль: password123")
            print(f"  Уровень: Адепт")
            print(f"  Корзина: {test_cart.total_items} товара на {test_cart.total_price} галлеонов")
            print()
            print("🧪 ДОСТУПНЫЕ ЗЕЛЬЯ:")
            print(f"  Всего: {len(potions_map)} зелий")
            print(f"  Категорий: {len(categories_map)}")
            print(f"  В наличии: {sum(1 for p in potions_map.values() if p.in_stock)}")
            print("-" * 40)
            print("\n🎮 ДАЛЕЕ:")
            print("1. Запустите сервер: uvicorn main:app --reload --port 8001")
            print("2. Откройте http://127.0.0.1:8001/docs")
            print("3. Используйте кнопку 'Authorize' для входа")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при заполнении базы данных: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    asyncio.run(seed_database())