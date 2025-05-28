// API utilities
const api = {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    async get(endpoint) {
        return this.request(endpoint);
    },
    
    async post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    },
    
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};

// UI utilities
const ui = {
    showMessage(message, type, elementId = 'message') {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = message;
            element.className = `alert alert-${type} fade-in`;
            element.classList.remove('d-none');
            
            // Auto-hide success messages after 3 seconds
            if (type === 'success') {
                setTimeout(() => {
                    element.classList.add('d-none');
                }, 3000);
            }
        }
    },
    
    showLoading(elementId, message = 'Loading...') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="text-center">
                    <div class="loading-spinner mx-auto mb-3"></div>
                    <p>${message}</p>
                </div>
            `;
        }
    },
    
    escapeHTML(str) {
        if (typeof str !== 'string') return '';
        return str.replace(/[&<>'"]/g, tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag]));
    },
    
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
};

// Auth utilities
const auth = {
    async logout() {
        try {
            await api.post('/api/auth/logout');
            window.location.href = '/login';
        } catch (error) {
            ui.showMessage('Logout failed. Please try again.', 'danger');
        }
    },
    
    async login(email, password) {
        try {
            await api.post('/api/auth/login', { email, password });
            window.location.href = '/dashboard';
        } catch (error) {
            throw new Error(error.message || 'Login failed');
        }
    },
    
    async register(name, email, password) {
        try {
            const response = await api.post('/api/auth/register', {
                name,
                email,
                password
            });
            return response;
        } catch (error) {
            throw new Error(error.message || 'Registration failed');
        }
    }
};

// File utilities
const fileManager = {
    async uploadFile(formData) {
        try {
            const response = await fetch('/api/files/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            return data;
        } catch (error) {
            throw new Error(error.message || 'File upload failed');
        }
    },
    
    async deleteFile(fileId) {
        try {
            await api.delete(`/api/files/${fileId}`);
        } catch (error) {
            throw new Error(error.message || 'File deletion failed');
        }
    },
    
    async loadFiles() {
        try {
            const data = await api.get('/api/files/files');
            return data.files;
        } catch (error) {
            throw new Error(error.message || 'Failed to load files');
        }
    }
}; 