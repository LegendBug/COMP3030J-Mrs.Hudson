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

    console.log("Right-clicked on: ", item.closest('.accordion-item')); // Debug: 查看右键点击的元素

    // Hide context menu on any other click
    document.addEventListener('click', function () {
        contextMenu.style.display = 'none';
    }, {once: true});
}

function createFabricElement() {
    // 正确获取当前Accordion项的body部分
    const contextMenu = document.getElementById('contextMenu');
    if (!contextMenu.relatedTarget) {
        console.error('No target layer found!');
        return;
    }
    const accordionBody = contextMenu.relatedTarget.querySelector('.accordion-body');
    if (!accordionBody) {
        console.error('Accordion body not found!');
        return;
    }

    // 创建新的Element按钮
    const newButton = document.createElement('button');
    newButton.textContent = 'New Element';
    newButton.className = 'btn element-btn mt-2';
    newButton.style.width = '100%'; // 确保按钮宽度适配其容器
    // 为新按钮添加右键菜单的事件监听
    newButton.addEventListener('contextmenu', function (event) {
        event.preventDefault();
        showElementContextMenu(event, newButton);
    });

    // 将新创建的按钮添加到正确的Accordion层级的body中
    accordionBody.appendChild(newButton);
}


function createLayer() {
    // 获取当前激活的Accordion的Body部分
    const contextMenu = document.getElementById('contextMenu');
    if (!contextMenu.relatedTarget) {
        console.error('No target layer for creating new layer');
        return;
    }
    const parentAccordionItem = contextMenu.relatedTarget; // 直接获取手风琴项
    const parentAccordionBody = parentAccordionItem.querySelector('.accordion-body');
    if (!parentAccordionBody) {
        console.error('Parent accordion body not found!');
        return;
    }

    console.log("Creating a new layer inside: ", parentAccordionBody); // Debug: 查看当前操作的父级元素


    // 确保每个新的手风琴项都包含自己的折叠区域
    const newAccordionItem = document.createElement('div');
    newAccordionItem.className = 'accordion-item';
    const newAccordionHeader = document.createElement('h2');
    newAccordionHeader.className = 'accordion-header';
    const uniqueId = `subHeading-${Math.random().toString(36).substr(2, 9)}`;
    const newCollapseButton = document.createElement('button');
    newCollapseButton.className = 'accordion-button collapsed';
    newCollapseButton.setAttribute('data-bs-toggle', 'collapse');
    newCollapseButton.setAttribute('data-bs-target', `#${uniqueId}`);
    newCollapseButton.textContent = 'New Layer';
    newAccordionHeader.appendChild(newCollapseButton);
    const newAccordionCollapse = document.createElement('div');
    newAccordionCollapse.id = uniqueId;
    newAccordionCollapse.className = 'accordion-collapse collapse';
    const newAccordionBody = document.createElement('div');
    newAccordionBody.className = 'accordion-body';

    newAccordionCollapse.appendChild(newAccordionBody);
    newAccordionItem.appendChild(newAccordionHeader);
    newAccordionItem.appendChild(newAccordionCollapse);

    // 确保新手风琴项作为一个独立项添加
    parentAccordionBody.appendChild(newAccordionItem);

    // 确保新创建的子Accordion能够响应右键菜单
    newAccordionItem.addEventListener('contextmenu', function (event) {
        event.preventDefault();
        showContextMenu(event, newAccordionItem);
    });
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


