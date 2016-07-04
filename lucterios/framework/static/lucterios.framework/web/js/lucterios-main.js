/*global $ */

$(function () {
    
    $("button.lucterios-menu").click(function () {
        $("#navbar").toggleClass('visibleMenu');
    });
    $("a.switch-content").click(function () {
        $("div.content-container").hide();
        $("li.menu").removeClass("active");
        var divToShow = this.getAttribute("data");
        $("#" + divToShow).show();
        $(this).parent().addClass("active");
    });
});