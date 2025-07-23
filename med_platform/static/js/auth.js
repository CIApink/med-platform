/**
 * 用户认证相关的JavaScript函数
 */

// 更新认证UI显示
function updateAuthUI() {
    // 检查是否有用户登录
    fetch('/user-status/')
        .then(response => response.json())
        .then(data => {
            const loginSignup = document.querySelector('.login-signup');
            const userEmail = document.querySelector('.user-email');
            
            if (data.is_authenticated) {
                // 用户已登录，显示邮箱和注销选项
                if (loginSignup) loginSignup.style.display = 'none';
                if (userEmail) {
                    userEmail.textContent = `${data.email} (点击注销)`;
                    userEmail.style.display = 'block';
                }
            } else {
                // 用户未登录，显示登录/注册选项
                if (loginSignup) loginSignup.style.display = 'block';
                if (userEmail) userEmail.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('获取用户状态失败:', error);
        });
}

// 注销功能
function logout() {
    fetch('/logout/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            // 注销成功，刷新页面
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('注销失败:', error);
    });
}

// 获取CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
