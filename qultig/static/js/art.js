// Art JS file
"use strict";

var current = 0;
var asked = 0;
var items = [];
var score = 0;
var moving = false;

var setup = function () {
    // Collection quizzes
    items = $(".mcq_item");

    // Setup navigation buttons
    $("#button_next").on("click", function () {
        next();
    });

    $("#button_previous").on("click", function () {
        previous();
    });

    // Lock carousel while moving
    var carousel = $('#quiz_carousel');
    carousel.on('slide.bs.carousel', function () {
        moving = true;
    });
    carousel.on('slid.bs.carousel', function () {
        moving = false;
    });

    // Setup MCQ buttons
    items.each(function () {
        $(this).find(".mcq_button").each(function () {
            $(this).click(make_choice);
        });
    });

    // Activate first quiz
    items.eq(0).addClass("active");

    make_mcq_buttons_equal_size();
    setup_popover(0);
    update_navigators();
    update_progress();
};

var enable_info = function () {
    items.eq(current).find('.mcq_thumbnail').attr("data-toggle", "collapse");
};

var collapse_info = function () {
    $('.mcq_info').collapse('hide');
};

var setup_popover = function (index) {
    items.eq(index).find(".mcq_button").each(function () {
        $(this).attr("data-toggle", "popover");
    });

    $('[data-toggle="popover"]').popover();

    $(document).on('click', function (e) {
        $('[data-toggle="popover"],[data-original-title]').each(function () {
            //the 'is' for buttons that trigger popups
            //the 'has' for icons within a button that triggers a popup
            if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                (($(this).popover('hide').data('bs.popover') || {}).inState || {}).click = false  // fix for BS 3.3.6
            }

        });
    });
};

var next = function () {
    move(true);
};

var previous = function () {
    move(false);
};

var move = function(next) {
    if (moving) {
        return;
    }

    collapse_info();

    if (next) {
        $("#quiz_carousel").carousel("next");
        current += 1;
    } else {
        $("#quiz_carousel").carousel("prev");
        current -= 1;
    }

    make_mcq_buttons_equal_size();
    update_navigators();
    update_progress();
};

var update_navigators = function () {
    if (current >= asked || current >= items.length - 1) {
        disable_next();
    } else {
        enable_next();
    }

    if (current <= 0) {
        disable_previous();
    } else {
        enable_previous();
    }
};

var update_progress = function () {
    var numerator = current + 1;
    var progress = numerator / items.length * 100;

    var progress_bar = $('.progress-bar');
    progress_bar.attr('aria-valuenow', progress).css('width', progress + '%');
    progress_bar.text(numerator + ' / ' + items.length)
};

var disable_navigators = function () {
    disable_previous();
    disable_next();
};

var disable_next = function () {
    disable_button($("#button_next"));
};

var enable_next = function () {
    enable_button($("#button_next"));
};

var disable_previous = function () {
    disable_button($("#button_previous"));
};

var enable_previous = function () {
    enable_button($("#button_previous"));
};

var enable_button = function (button) {
    button.attr("disabled", false);
    button.removeClass("disabled");
};

var disable_button = function (button) {
    button.attr("disabled", true);
    button.addClass("disabled");
};

var make_choice = function () {
    disable_mcq_buttons();
    disable_navigators();
    submit_answer(this);
    enable_info();
};

var submit_answer = function (button) {
    $.ajax({
        url: "/evaluate_art",
        type: "POST",
        data: {
            "item_id": items.eq(asked).attr('item_id'),
            "option_id": $(button).attr('option_id')
        },
        dataType: "json",
        success: function (response) {
            process_response(response);
        },
        error: function (error) {
            console.warn(error);
        },
        async: true
    });
};

// Process servers response
var process_response = function (response) {
    asked += 1;
    score += response.correct;
    color_mcq_buttons(response.labels);
    update_navigators();

    if (asked === items.length) {
        show_report();
    }
};

// Show report once all items are answered
var show_report = function () {
    var rate = score / items.length;
    var ratio = score + " / " + items.length;

    var message;
    var type;
    if (rate > 0.90) {
        message = "<b>Congratulations</b>, you got " + ratio + " questions right! You're awesome!";
        type = "alert-success";
    } else if (rate > 0.8) {
        message = "<b>Well done</b>, you got " + ratio + " questions right!";
        type = "alert-success";
    } else if (rate > 0.4) {
        message = "You got " + ratio + " questions right - not bad!";
        type = "alert-info";
    } else {
        message = "<b>Whoops</b>, you got " + ratio + " questions right - try again!";
        type = "alert-warning";
    }

    var reportElement = $("#report");
    reportElement.html("<p>" + message + "</p>");
    reportElement.addClass(type);
    $("#report-modal").modal("show");
};

var disable_mcq_buttons = function () {
    items.eq(current).find(".mcq_button").each(function () {
        $(this).prop("disabled", true);
    });
};

// Color buttons of choices
var color_mcq_buttons = function (labels) {
    for (var key in labels) {
        // check if the property/key is defined in the object itself, not in parent
        if (labels.hasOwnProperty(key)) {
            var button = items.eq(current).find(".mcq_button[option_id='" + key + "']");
            if (labels[key]) {
                button.addClass("btn-success");
            } else {
                button.addClass("btn-danger");
            }
        }
    }
};

// Make sure all choice boxes have the same height
var make_mcq_buttons_equal_size = function () {
    var highestBox = 0;
    var mcq_buttons = items.eq(current).find(".mcq_button");

    mcq_buttons.each(function (index, value) {
        var height = $(value).height();
        if (height > highestBox) {
            highestBox = height;
        }
    });

    mcq_buttons.each(function (index, value) {
        $(value).height(highestBox);
    });
};

// Hook
qultig.art = function () {
    $(document).ready(setup);
};
