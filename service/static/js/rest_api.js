
$(function () {

    // ****************************************
    // UTILITY FUNCTIONS
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_description").val(res.description);
        $("#product_available").val(res.available ? "true" : "false");
        $("#product_category").val(res.category);
        $("#product_price").val(Number(res.price).toFixed(2));
    }

    // Clears all form fields except Product ID
    function clear_form_data() {
        $("#product_name").val("");
        $("#product_description").val("");
        $("#product_available").val("");
        $("#product_category").val("");
        $("#product_price").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty().append(message);
    }

    // Displays an error message safely
    function show_error(res) {
        let message = "Server error!";

        if (res.responseJSON && res.responseJSON.message) {
            message = res.responseJSON.message;
        }

        flash_message(message);
    }


    // ****************************************
    // CREATE A PRODUCT
    // ****************************************

    $("#create-btn").click(function () {

        let data = {
            name: $("#product_name").val(),
            description: $("#product_description").val(),
            available: $("#product_available").val() === "true",
            category: $("#product_category").val(),
            price: $("#product_price").val()
        };

        $("#flash_message").empty();

        $.ajax({
            type: "POST",
            url: "/products",
            contentType: "application/json",
            data: JSON.stringify(data)
        })
        .done(function (res) {
            update_form_data(res);
            flash_message("Success");
        })
        .fail(function (res) {
            show_error(res);
        });
    });


    // ****************************************
    // UPDATE A PRODUCT
    // ****************************************

    $("#update-btn").click(function () {

        let product_id = $("#product_id").val();

        let data = {
            name: $("#product_name").val(),
            description: $("#product_description").val(),
            available: $("#product_available").val() === "true",
            category: $("#product_category").val(),
            price: $("#product_price").val()
        };

        $("#flash_message").empty();

        $.ajax({
            type: "PUT",
            url: `/products/${product_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })
        .done(function (res) {
            update_form_data(res);
            flash_message("Success");
        })
        .fail(function (res) {
            show_error(res);
        });
    });


    // ****************************************
    // RETRIEVE A PRODUCT
    // ****************************************

    $("#retrieve-btn").click(function () {

        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        $.ajax({
            type: "GET",
            url: `/products/${product_id}`,
            contentType: "application/json"
        })
        .done(function (res) {
            update_form_data(res);
            flash_message("Success");
        })
        .fail(function (res) {
            clear_form_data();
            show_error(res);
        });
    });


    // ****************************************
    // DELETE A PRODUCT
    // ****************************************

    $("#delete-btn").click(function () {

        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        $.ajax({
            type: "DELETE",
            url: `/products/${product_id}`,
            contentType: "application/json"
        })
        .done(function () {
            clear_form_data();
            $("#product_id").val("");
            $("#search_results").empty();
            flash_message("Success");
        })
        .fail(function (res) {
            show_error(res);
        });
    });


    // ****************************************
    // CLEAR THE FORM
    // ****************************************

    $("#clear-btn").click(function () {

        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });


    // ****************************************
    // SEARCH FOR PRODUCTS
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#product_name").val();
        let description = $("#product_description").val();
        let available = $("#product_available").val();
        let category = $("#product_category").val();

        // Build search parameters
        let params = {};

        if (name) {
            params.name = name;
        }

        if (description) {
            params.description = description;
        }

        if (available !== "") {
            params.available = available;
        }

        if (category && category !== "UNKNOWN") {
            params.category = category;
        }

        $("#flash_message").empty();

        $.ajax({
            type: "GET",
            url: "/products",
            data: params,
            contentType: "application/json"
        })
        .done(function (res) {

            $("#search_results").empty();

            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">ID</th>';
            table += '<th class="col-md-2">Name</th>';
            table += '<th class="col-md-2">Description</th>';
            table += '<th class="col-md-2">Available</th>';
            table += '<th class="col-md-2">Category</th>';
            table += '<th class="col-md-2">Price</th>';
            table += '</tr></thead><tbody>';

            let firstProduct = null;

            for (let i = 0; i < res.length; i++) {

                let product = res[i];

                table += `<tr id="row_${i}">
                    <td>${product.id}</td>
                    <td>${product.name}</td>
                    <td>${product.description}</td>
                    <td>${product.available}</td>
                    <td>${product.category}</td>
                    <td>${Number(product.price).toFixed(2)}</td>
                </tr>`;

                if (i === 0) {
                    firstProduct = product;
                }
            }

            table += '</tbody></table>';

            $("#search_results").append(table);

            // Copy the first result into the form
            if (firstProduct !== null) {
                update_form_data(firstProduct);
            }

            flash_message("Success");
        })
        .fail(function (res) {
            show_error(res);
        });
    });

});
