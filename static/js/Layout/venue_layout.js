/*悬浮按钮和侧边栏的交互逻辑*/
let floatingActionButton = document.getElementById('add-venue-btn');
let offcanvas = document.getElementById('offcanvasScrolling');
let bsOffcanvas = new bootstrap.Offcanvas(offcanvas);
let isOffcanvasAnimating = false; // 添加一个flag来跟踪offcanvas的状态

// 当offcanvas开始打开时
offcanvas.addEventListener('show.bs.offcanvas', function () {
    isOffcanvasAnimating = true;
    floatingActionButton.style.visibility = 'hidden';
    floatingActionButton.querySelector('i').classList.remove('fa-chevron-right');
    floatingActionButton.querySelector('i').classList.add('fa-chevron-left');
});

// 当offcanvas完全打开后
offcanvas.addEventListener('shown.bs.offcanvas', function () {
    floatingActionButton.style.transform = 'translateX(' + offcanvas.offsetWidth + 'px)';
    isOffcanvasAnimating = false;
    floatingActionButton.style.visibility = 'visible';
});

// 当offcanvas开始关闭时
offcanvas.addEventListener('hide.bs.offcanvas', function () {
    floatingActionButton.style.visibility = 'hidden';
    isOffcanvasAnimating = true;
});

// 当offcanvas完全关闭后
offcanvas.addEventListener('hidden.bs.offcanvas', function () {
    floatingActionButton.style.transform = 'none';
    floatingActionButton.querySelector('i').classList.remove('fa-chevron-left');
    floatingActionButton.querySelector('i').classList.add('fa-chevron-right');
    isOffcanvasAnimating = false;
    floatingActionButton.style.visibility = 'visible';
});

// 修改悬浮按钮的点击事件处理程序
floatingActionButton.addEventListener('click', function () {
    if (isOffcanvasAnimating) return; // 如果offcanvas正在动画中，则不做任何操作
    if (bsOffcanvas._isShown) {
        bsOffcanvas.hide();
    } else {
        bsOffcanvas.show();
    }
});
// ----------------------------------------------------------------------------------------------------------------------------