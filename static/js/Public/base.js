$(document).ready(function () {
    $('.toast-message').each(function() {
        var message = $(this).data('message');
        var tag = $(this).data('tag');
        var toastClass = '';
        switch(tag) {
            case 'success':
                toastClass = 'toast-success';
                break;
            case 'warning':
                toastClass = 'toast-warning';
                break;
            case 'error':
                toastClass = 'toast-error';
                break;
            default:
                toastClass = 'toast-info'; // 默认样式
        }

        var toastHtml = `
            <div class="toast ${toastClass}" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3000">
                <div class="toast-header">
                    <strong class="me-auto">Message</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        $('#toast-container').append(toastHtml);
    });

    $('.toast').toast('show');
});
