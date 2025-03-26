// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// Состояние приложения
let state = {
    cart: [],
    products: [],
    categories: []
};

// DOM элементы
const elements = {
    categoriesContainer: document.getElementById('categories'),
    cartCount: document.getElementById('cart-count'),
    cartItems: document.getElementById('cart-items'),
    totalPrice: document.getElementById('total-price'),
    cart: document.getElementById('cart'),
    productModal: document.getElementById('product-modal'),
    modalImage: document.getElementById('modal-image'),
    modalName: document.getElementById('modal-name'),
    modalDescription: document.getElementById('modal-description'),
    modalPrice: document.getElementById('modal-price'),
    quantity: document.getElementById('quantity')
};

// Текущий выбранный товар
let currentProduct = null;
let currentQuantity = 1;

// Инициализация приложения
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    renderCategories();
    updateCartCount();
});

// Загрузка данных с сервера
async function loadData() {
    try {
        const [categoriesRes, featuredRes] = await Promise.all([
            fetch('/api/main-categories'),
            fetch('/api/products/featured')
        ]);
        
        state.categories = await categoriesRes.json();
        state.products = await featuredRes.json();
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
    }
}

// Рендер категорий и товаров
function renderCategories() {
    let html = '';
    
    state.categories.forEach(category => {
        const categoryProducts = state.products.filter(p => p.category_id === category.id);
        if (categoryProducts.length === 0) return;
        
        html += `
            <div class="category-section">
                <h2 class="category-title">${category.name}</h2>
                <div class="products-grid">
                    ${categoryProducts.map(product => `
                        <div class="product-card" onclick="openProductModal(${product.id})">
                            <img src="${product.image_url}" alt="${product.name}" class="product-image">
                            <div class="product-info">
                                <h3 class="product-name">${product.name}</h3>
                                <p class="product-price">${product.price} ₽</p>
                                <p class="product-description">${product.description.substring(0, 60)}...</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    elements.categoriesContainer.innerHTML = html;
}

// Работа с модальным окном товара
function openProductModal(productId) {
    currentProduct = state.products.find(p => p.id === productId);
    if (!currentProduct) return;
    
    currentQuantity = 1;
    
    elements.modalImage.src = currentProduct.image_url;
    elements.modalName.textContent = currentProduct.name;
    elements.modalDescription.textContent = currentProduct.description;
    elements.modalPrice.textContent = `${currentProduct.price} ₽`;
    elements.quantity.textContent = currentQuantity;
    
    elements.productModal.style.display = 'flex';
}

function closeModal() {
    elements.productModal.style.display = 'none';
}

function changeQuantity(change) {
    currentQuantity = Math.max(1, currentQuantity + change);
    elements.quantity.textContent = currentQuantity;
}

// Работа с корзиной
function toggleCart() {
    elements.cart.style.display = elements.cart.style.display === 'block' ? 'none' : 'block';
    if (elements.cart.style.display === 'block') {
        renderCart();
    }
}

function addToCart() {
    if (!currentProduct) return;
    
    const existingItem = state.cart.find(item => item.product_id === currentProduct.id);
    
    if (existingItem) {
        existingItem.quantity += currentQuantity;
    } else {
        state.cart.push({
            product_id: currentProduct.id,
            quantity: currentQuantity,
            product: currentProduct
        });
    }
    
    updateCartCount();
    closeModal();
    
    // Сохраняем корзину в localStorage
    localStorage.setItem('cart', JSON.stringify(state.cart));
}

function renderCart() {
    if (state.cart.length === 0) {
        elements.cartItems.innerHTML = '<p>Ваша корзина пуста</p>';
        elements.totalPrice.textContent = '0';
        return;
    }
    
    let total = 0;
    let itemsHtml = '';
    
    state.cart.forEach(item => {
        const itemTotal = item.product.price * item.quantity;
        total += itemTotal;
        
        itemsHtml += `
            <div class="cart-item">
                <img src="${item.product.image_url}" alt="${item.product.name}">
                <div class="cart-item-info">
                    <h4>${item.product.name}</h4>
                    <p>${item.product.price} ₽ × ${item.quantity} = ${itemTotal} ₽</p>
                    <button onclick="removeFromCart(${item.product_id})">Удалить</button>
                </div>
            </div>
        `;
    });
    
    elements.cartItems.innerHTML = itemsHtml;
    elements.totalPrice.textContent = total;
}

function removeFromCart(productId) {
    state.cart = state.cart.filter(item => item.product_id !== productId);
    updateCartCount();
    renderCart();
    
    // Обновляем localStorage
    localStorage.setItem('cart', JSON.stringify(state.cart));
}

function updateCartCount() {
    const count = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    elements.cartCount.textContent = count > 0 ? count : '';
}

// Инициализация корзины из localStorage
function initCartFromStorage() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
        state.cart = JSON.parse(savedCart);
        updateCartCount();
    }
}

// Вызываем инициализацию корзины при загрузке
initCartFromStorage();

// Обработка оформления заказа
document.querySelector('.checkout-btn')?.addEventListener('click', () => {
    if (state.cart.length === 0) return;
    
    const orderData = {
        products: state.cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
        })),
        total: state.cart.reduce((sum, item) => sum + (item.product.price * item.quantity), 0)
    };
    
    // Здесь можно добавить отправку заказа на сервер
    alert(`Заказ оформлен! Сумма: ${orderData.total} ₽`);
    state.cart = [];
    updateCartCount();
    renderCart();
    localStorage.removeItem('cart');
});