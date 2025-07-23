/* 统一导航栏JavaScript功能 */
function logout() {
    if (confirm('确定要注销吗？')) {
        // 使用相对路径，让Django处理URL路由
        window.location.href = "/logout/";
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 这里的用户认证状态逻辑将由各个页面的具体模板处理
    // 因为需要访问Django的模板变量
});
