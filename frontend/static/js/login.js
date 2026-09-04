const API_URL = window.location.origin;
const DASHBOARD_URL = '/dashboard';

let isRedirecting = false;

const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginButton = document.getElementById('loginButton');
const buttonText = document.getElementById('buttonText');
const buttonSpinner = document.getElementById('buttonSpinner');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const togglePassword = document.getElementById('togglePassword');

const registerModal = document.getElementById('registerModal');
const registerLink = document.getElementById('registerLink');
const closeRegister = document.getElementById('closeRegister');
const registerForm = document.getElementById('registerForm');

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    if (token && !isRedirecting) {
        verifyToken(token);
    }
});

togglePassword.addEventListener('click', function() {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    togglePassword.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
});

loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    
    if (!username || !password) {
        showError('Por favor, completa todos los campos');
        return;
    }
    
    await loginUser(username, password);
});

async function loginUser(username, password) {
    if (isRedirecting) return;
    
    setLoading(true);
    hideError();
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(API_URL + '/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error al iniciar sesión');
        }
        
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type', data.token_type);
        
        console.log('Token guardado:', data.access_token); // Para debugging
        
        isRedirecting = true;
        window.location.href = DASHBOARD_URL;
        
    } catch (error) {
        console.error('Error en login:', error);
        showError(error.message || 'Usuario o contraseña incorrectos');
        setLoading(false);
        passwordInput.value = '';
        passwordInput.focus();
    }
}

async function verifyToken(token) {
    if (isRedirecting) return;
    
    try {
        const response = await fetch(API_URL + '/auth/me', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });
        
        if (response.ok) {
            isRedirecting = true;
            window.location.href = DASHBOARD_URL;
        } else {
            console.log('Token inválido, eliminando...');
            localStorage.removeItem('access_token');
            localStorage.removeItem('token_type');
        }
    } catch (error) {
        console.error('Error verificando token:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_type');
    }
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.classList.add('show');
}

function hideError() {
    errorMessage.style.display = 'none';
    errorMessage.classList.remove('show');
}

function setLoading(loading) {
    if (loading) {
        loginButton.disabled = true;
        buttonText.style.display = 'none';
        buttonSpinner.style.display = 'inline-block';
        loginButton.innerHTML = '⏳ Procesando...';
    } else {
        loginButton.disabled = false;
        buttonText.style.display = 'inline';
        buttonSpinner.style.display = 'none';
        loginButton.innerHTML = 'Iniciar Sesión';
    }
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !loginButton.disabled) {
        loginForm.dispatchEvent(new Event('submit'));
    }
});

registerLink.addEventListener('click', function(e) {
    e.preventDefault();
    registerModal.style.display = 'flex';
});

closeRegister.addEventListener('click', function() {
    registerModal.style.display = 'none';
});

registerModal.addEventListener('click', function(e) {
    if (e.target === registerModal) {
        registerModal.style.display = 'none';
    }
});

registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    
    if (!username || !email || !password || !confirmPassword) {
        showRegisterError('Por favor, completa todos los campos');
        return;
    }
    
    if (password.length < 6) {
        showRegisterError('La contraseña debe tener al menos 6 caracteres');
        return;
    }
    
    if (password !== confirmPassword) {
        showRegisterError('Las contraseñas no coinciden');
        return;
    }
    
    if (!email.includes('@') || !email.includes('.')) {
        showRegisterError('Ingresa un email válido');
        return;
    }
    
    const registerError = document.getElementById('registerError');
    registerError.style.display = 'none';
    
    try {
        const response = await fetch(API_URL + '/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            let errorMsg = data.detail || 'Error al registrar usuario';
            if (typeof data.detail === 'object') {
                errorMsg = data.detail.map(function(err) { return err.msg; }).join(', ');
            }
            throw new Error(errorMsg);
        }
        
        alert('¡Usuario registrado exitosamente! Ahora puedes iniciar sesión.');
        registerModal.style.display = 'none';
        registerForm.reset();
        usernameInput.value = username;
        passwordInput.focus();
        
    } catch (error) {
        console.error('Error en registro:', error);
        showRegisterError(error.message);
    }
});

function showRegisterError(message) {
    const registerError = document.getElementById('registerError');
    registerError.textContent = message;
    registerError.style.display = 'block';
}