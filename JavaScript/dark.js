// 函数来更改元素的样式
function updateElementStyle(el) {
    el.style.backgroundColor = '#1e1e1e';
    el.style.color = 'white';
}

// 使用MutationObserver监听DOM变化
var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
            // 确保它是元素节点
            if (node.nodeType === 1) {
                updateElementStyle(node);
                // 如果新添加的节点包含子节点，也对它们应用样式
                node.querySelectorAll('*').forEach(updateElementStyle);
            }
        });
    });
});

// 配置观察选项
var config = { childList: true, subtree: true };

// 开始观察文档树，以观察后续的变化
observer.observe(document.body, config);

// 初始化时应用样式
document.querySelectorAll('*').forEach(updateElementStyle);
