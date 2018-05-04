$(document).ready(function () {
    namespace = '/test'; // change to an empty string to use the global namespace

    var entityMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': '&quot;',
        "'": '&#39;',
        "/": '&#x2F;'
    };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'\/]/g, function (s) {
            return entityMap[s];
        });
    }

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    socket.emit('get_draft_types');

    var username = "";
    var draft_id = "";

    socket.on('draft_types_update', function (msg) {
        log_message(msg);
        $('#draft_types').find('option').remove();
        msg.forEach(function (value, key, list) {
            var optionElement = $('<option value="' + value['id'] + '">' + value['name'] + '</option>');
            if (value['selected']) {
                optionElement.attr('selected', 'selected');
            }
            $('#draft_type').append(optionElement);
        });
    });

    socket.on('create_success', function (msg) {
        log_message(msg);
        console.log('got join success message');
        var room_id = msg['room_id'];
        DOM.goToRoom();


        $('#room').html(`You are in room <b>${room_id}</b>.  Give this room code to your opponent.<br />The draft type is:${msg['draft_type']}.<br />`);
    });

    socket.on('join_success', function (msg) {
        log_message(msg);
        console.log('joined room');
        var room_id = msg['room_id'];
        DOM.goToRoom();
        $('#room').html('You are in room <b>' + room_id + '</b><br />The draft type is: ' + msg['draft_type'] + '.<br />');
    });

    socket.on('join_error', function (msg) {
        log_message(msg);
        $('#join_error').html(escapeHtml(msg['message']));
    });

    socket.on('room_broadcast', function (msg) {
        log_message(msg);
        console.log('handling room broadcast');
        var roomEl = $('#room');
        roomEl.append(escapeHtml(msg['msg']));
        roomEl.append('<br />');
    });

    socket.on('draft_start', function (msg) {
        log_message(msg);

        console.log('handling draft start');

        draft_id = msg['room_id'];

       
        $('#draft_container').css('display', 'block');

        var $coin_flip_el = $('#coin_flip');

        if (username === msg['player_one']) {
            $coin_flip_el.html("Waiting for coin flip...");
        }

        $coin_flip_el.show();

        $('#map_pool').append($('<h3>Map Pool</h3>'));
        $('#map_pool').append($('<div class="row"></div>'))
        msg['map_pool'].forEach((value, key, list) => {
            let family = value['family'];
            let name = value['name'];
            var mapElement = $(`<div class='map col-3'><img class="map-thumbnail" src="static/img/${family}.png"/><h5 class="text-center">${name}</h5></div>`);
            $('#map_pool .row').append(mapElement);
        });
    });


    socket.on('coin_chosen', (message) => {
        log_message(message);

        var $coin_flip_el = $('#coin_flip');

        if (username === message['player_one']) {
            $coin_flip_el.html(`Waiting for coin flip... ${message['message']}`);
        }
    });

    socket.on('flip_winner', function (message) {
        log_message(message);
        
        DOM.flipCoin(message['flip_result']).then(done => {
            if (username != message['winner']) {
                $('#first_option_msg').html("You have lost the coin flip.  Waiting on opponent");
            } else {
                $('#first_option').show();
                $('#coin_flip').hide();
            }
        });
    });


    socket.on('winner_deferred', function (message) {
        log_message(message);
        var first_option_el = $('#first_option');

        $('#first_option_msg').show();

        if (username != message['picker']) {
            first_option_el.html("You have deferred your pick.  Waiting on opponent...");
        } else {
            $('#first_option_header').html("Your opponent has deferred their pick.  Take your pick.");
            $('#first_defer_radio').remove();
        }

        first_option_el.show();

    });

    socket.on('select_spy_order', function (message) {
        log_message(message);

        var el = $('#second_option_spy_order');

        if (username == message['username']) {
            $('#spy_order_message').html("<h3>" + message['message'] + "</h3>");
        } else {
            el.html("Waiting on opponent to pick spy order...");
        }
        $('#coin_flip').hide();

        el.show();
    });

    socket.on('select_pick_order', function (message) {
        log_message(message);

        var el = $('#second_option_pick_order');

        if (username == message['username']) {
            $('#pick_order_message').html("<h3>" + message['message'] + "</h3>");
        } else {
            el.html("Waiting on opponent to pick selection order...");
        }

        el.css('display', 'inline');
    });

    var redraw_picks_bans = function (message) {
        $('#draft_bans').html('');

        message['banned_maps'].forEach(function (value, key, list) {
            var el = $('<li>' + escapeHtml(value['picker']) + ' has banned ' + value['map'] + '</li>');
            $('#draft_bans').append(el);
        });

        $('#draft_picks').html('');

        message['picked_maps'].forEach(function (value, key, list) {
            var el = $('<li>' + escapeHtml(value['picker']) + ' has selected ' + value['map'] + '</li>');
            $('#draft_picks').append(el);
        });
    };

    socket.on('draft_info', function (message) {
        log_message(message);

        //hide stuff we don't care about any more
        $('#create_form_wrapper').hide();
        $('#join_form_wrapper').hide();
        $('#room_info').hide();
        $('#coin_flip').hide();
        $('#second_option_pick_order').hide();
        $('#second_option_spy_order').hide();
        $('#first_option_msg').hide();

        $('#draft_info_draft_type').html("Draft type: " + escapeHtml(message['draft_type']) + "<br />");
        $('#draft_info_current_player').html("Current player: " + escapeHtml(message['current_player']) + "<br />");
        $('#draft_info_start_player').html("First selection: " + escapeHtml(message['start_player']) + "<br />");
        $('#draft_info_first_spy').html("First spy: " + escapeHtml(message['first_spy']) + "<br />");
        $('#draft_info_state').html("DRAFT STATE: " + message['state'] + "<br />");

        redraw_picks_bans(message);

        var userMessage;

        $('#draft_form_options').html('');

        //<label for="map_choice_' + value['slug'] + '">' + value['name'] + '</label><br />

        if (message['current_player'] == username) {
            message['map_pool'].forEach((value, key, list) => {
                //console.log(value['name'] + " -> " + value['slug']);
                let slug = value['slug'];
                let family = value['family'];
                let name = value['name'];

                let radioButton = $(`<label class="map-label col-3"><input type="radio" name="map_choice" value="${slug}" id="map_choice_${slug}" class="map-radio"/><img src="static/img/${family}.png"/><h5 class="text-center">${name}</h5></label>`);
                $('#draft_form_options').append(radioButton);
            });


            $('#draft_form_options').removeClass('banning');
            $('#draft_form_options').removeClass('picking');
            if (message['state'].endsWith('BANNING')) {
                var noBan = $('<input type="radio" name="map_choice" value="nothing" id="map_choice_nothing" /><label for="map_choice_nothing">Refuse to ban</label><br />');
                $('#draft_form_options').append(noBan);
                $('#draft_form_options').addClass('banning');
            }else if (message['state'].endsWith('PICKING')){
                $('#draft_form_options').addClass('picking');
            }
            userMessage = "<h2>" + message['user_readable_state'] + "</h2>";
            $('#draft_form').show();
            $('#draft_container').hide();

        } else {
            userMessage = "<h2> Waiting for " + message['user_readable_state'] + "</h2>";
            $('#draft_form').hide();
            $('#draft_container').show();
        }

        $('#draft_form_message').html(userMessage);

        $('#draft_info').show();
    });

    socket.on('draft_over', function (message) {
        log_message(message);

        redraw_picks_bans(message);
        $('#draft_form').hide();
        $('#chat_form').hide();
        $('#draft_container').hide();
        $('#draft_info_state').text('Complete!');
        $('#draft_info_status').text('Drafting over !');
        socket.emit('disconnect_request', {room_id: draft_id});
    });

    socket.on('join_error', function (message) {
        log_message(msg);

        $('#join_error').html(message['message']);
    });

    var log_message = function (msg) {
        $('#log').append('<br>Received #' + msg.count + ': ' + JSON.stringify(msg));
        console.log('Received: ');
        console.log(msg);
    };

    socket.on('spectate_join_success', function (message) {
        $('#lobby').hide();
        $('#drafting').hide();

        $('#spectate_list_wrapper').css('display', 'inline');

        $('#room').html("you've joined room " + message['room_id']);
    });

    socket.on('spectator_update', function (message) {
        log_message(message);

        var spectateListEl = $('#spectate_list');
        spectateListEl.html('');

        message['events'].forEach(function (item, key, list) {
            spectateListEl.append('<li>' + item['msg'] + '</li>');
        });
    });

    socket.on('chat_event', function (message) {
        log_message(message);
        var user = escapeHtml(message['talker']);
        var text = escapeHtml(message['text']);
        var el = $('<b>' + user + '</b>: ' + text + ' </br>');
        $('#chat_log').append(el);
    });

    // event handler for server sent data
    // the data is displayed in the "Received" section of the page
    socket.on('my response', function (msg) {
        log_message(msg); // ????

        console.log('Server Response #' + msg.count + ': '  + msg.data);
        $('#log').append('<br>Received #' + msg.count + ': ' + JSON.stringify(msg)); //?????


    });

    // event handler for new connections
    socket.on('connect', function () {
        socket.emit('my event', {data: 'I\'m connected!'});
    });

    $('form#create').submit(function (event) {
        console.log('ok');
        username = $('#username').val();
        if (username == undefined || username === "") {
            return false;
        }
        socket.emit('create', {data: username, draft_type_id: $('#draft_type').val()});
        return false;
    });

    $('form#join_draft').submit(function (event) {
        console.log('attempting to join room');
        username = $('#join_username').val();
        if (username == undefined || username === "") {
            return false;
        }
        socket.emit('join_draft', {username: username, room_id: $('#join_room_id').val()});
        return false;
    });

    $('form#flip_form').submit(function (event) {
        console.log('flipping coin...');
        var f = $('input:radio[name=ht]').filter(":checked").val();
        if (f == undefined)
            return false;
        var flip_data =
        {
            username: username,
            room_id: draft_id,
            choice: f
        };
        console.log(flip_data);
        $("#coin_flip").css("display", "none");
        socket.emit('coin_flip', flip_data);
        return false;
    });

    $('form#first_option_form').submit(function (event) {
        console.log('putting choice up');
        var choice = $('input:radio[name=choice]').filter(":checked").val();
        if (choice == undefined)
            return false;
        var data = {
            username: username,
            room_id: draft_id,
            choice: choice
        };
        socket.emit('first_option_form', data);
        $('#first_option').hide();

        return false;
    });

    $('form#second_option_pick_form').submit(function (event) {
        var choice = $('input:radio[name=pick_choice]').filter(":checked").val();
        if (choice == undefined)
            return false;
        $('#second_option_pick_order').hide();

        var data = {
            username: username,
            room_id: draft_id,
            choice: choice
        };

        socket.emit('second_option_pick', data);

        return false;
    });

    $('form#second_option_spy_form').submit(function (event) {
        var choice = $('input:radio[name=spy_choice]').filter(":checked").val();
        if (choice == undefined)
            return false;
        $('#second_option_spy_order').hide();

        var data = {
            username: username,
            room_id: draft_id,
            choice: choice
        };

        socket.emit('second_option_spy', data);

        return false;
    });

    $('form#draft_form').submit(function (event) {
        var choice = $('input:radio[name=map_choice]').filter(":checked").val();
        if (choice == undefined)
            return false;
        console.log("got value " + choice);

        //var isPick = $('#pick_check').is(':checked')

        var data = {
            username: username,
            room_id: draft_id,
            choice: choice
        };
        socket.emit('draft_map', data);
        return false;
    });

    $('form#spectate_draft').submit(function (event) {
        var room_id = $('#spectate_room_id').val();
        if (room_id == undefined || room_id === "")
            return false;

        socket.emit('spectate_draft', {
            room_id: room_id
        });
        return false;
    });

    $('form#chat_form_form').submit(function (event) {
        var textEl = $('#chat_form_text');
        var text = textEl.val();
        if (text === "")
            return false; // don't send empty messages
        var data = {
            username: username,
            room_id: draft_id,
            chat_text: text
        };
        console.log('chatting ');
        console.log(data);
        textEl.val("");
        socket.emit('chat_message', data);
        return false;
    });
});
