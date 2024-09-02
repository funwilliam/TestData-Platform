(function () {
    // 設置頁面上下的padding，否則可能會被<header> or <footer> 遮擋
    function setPadding() {
        // document.getElementById('padding-top').style.height = `${document.getElementById('header').offsetHeight}px`;
        document.getElementById('padding-bottom').style.height = `${document.getElementById('footer').offsetHeight}px`;
    }

    function startup() {
        setPadding();
    }

    window.addEventListener('load', startup);
})();