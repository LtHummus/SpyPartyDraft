var DOM = (function () {
    
    return {

        flipCoin: async function(side){
            return new Promise((resolve, reject) => {
                $('#coin_container').show();
                $('#coin').removeClass();
                $('#coin').addClass(side);
                setTimeout(() => resolve(), 1500);
            })
        },

        goToRoom: function(){
            $('#scl-alert').hide();
            $('#lobby').hide();
            $('#room_header').show(); 
        },

        beginDraft: function() {
            $('#draft_info').show();
        },

        scrollChatToBottom : function (){
            const $chat = $('#chat_log');
            const height = $chat[0].scrollHeight;
            $chat.scrollTop(height)
        }
    }

})();