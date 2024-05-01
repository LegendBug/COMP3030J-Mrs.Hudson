/*悬浮按钮和侧边栏的交互逻辑*/
let floatingActionButton = document.getElementById('toggle-offcanvas-btn');
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
/*Layer Item的Context Menu 控制逻辑*/
function showContextMenu(event, item) {
    const contextMenu = document.getElementById('contextMenu');
    contextMenu.style.top = `${event.pageY}px`;
    contextMenu.style.left = `${event.pageX}px`;
    contextMenu.style.display = 'block';
    contextMenu.relatedTarget = item.closest('.accordion-item');

    // Hide context menu on any other click
    document.addEventListener('click', function () {
        contextMenu.style.display = 'none';
    }, {once: true});
}

function createFabricElement() {
    const contextMenu = document.getElementById('contextMenu');
    if (!contextMenu.relatedTarget) {
        console.error('No target layer found!');
        return;
    }

    const accordionBody = contextMenu.relatedTarget.querySelector('.accordion-collapse');
    if (accordionBody) {
        const newButton = document.createElement('button');
        newButton.textContent = 'New Element';
        newButton.className = 'btn element-btn mt-2';
        newButton.addEventListener('contextmenu', function (event) {
            event.preventDefault();
            showElementContextMenu(event, newButton);
        });
        accordionBody.appendChild(newButton);
    } else {
        console.error('Accordion body not found!');
    }
}

function deleteLayer() {
    const contextMenu = document.getElementById('contextMenu');
    if (contextMenu.relatedTarget) {
        contextMenu.relatedTarget.remove();
    }
}

function renameLayer() {
    const contextMenu = document.getElementById('contextMenu');
    let newName = prompt("Enter new name for the layer:");
    if (newName && contextMenu.relatedTarget) {
        const header = contextMenu.relatedTarget.querySelector('.accordion-header button');
        if (header) {
            header.textContent = newName;
        }
    }
}

function addBackground() {
    const contextMenu = document.getElementById('contextMenu');
    if (contextMenu.relatedTarget) {
        const accordionBody = contextMenu.relatedTarget.querySelector('.accordion-body');
        if (accordionBody) {
            accordionBody.style.backgroundImage = 'url(https://example.com/new-background.jpg)';
        }
    }
}

// ----------------------------------------------------------------------------------------------------------------------------
/*Element Item的Context Menu 控制逻辑*/
function showElementContextMenu(event, btn) {
    const elementMenu = document.getElementById('elementMenu'); // 获取Element的右键菜单
    if (!elementMenu) {
        console.error('Element menu not found!');
        return;
    }
    elementMenu.style.top = `${event.pageY}px`;
    elementMenu.style.left = `${event.pageX}px`;
    elementMenu.style.display = 'block';
    elementMenu.relatedTarget = btn;  // 将目标按钮设置为相关目标

    // 点击其他地方时隐藏菜单
    document.addEventListener('click', function () {
        elementMenu.style.display = 'none';
    }, {once: true});
}


