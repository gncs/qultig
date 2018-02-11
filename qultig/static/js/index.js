// Main JS file
"use strict";

// Initialize app namespace
var qultig = {};

var init_sidebar = function () {
    $("[data-toggle=offcanvas]").click(function () {
        $(".row-offcanvas").toggleClass("active");
    });
};

$(document).ready(init_sidebar);