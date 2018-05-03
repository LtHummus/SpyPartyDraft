
$(document).ready(() => {
    $.get('static/changelog.xml', (changelog) => {
        $(changelog).find('changeSet').each((index, changeSet) => {
            let version = $(changeSet).attr('version');
            let $changeSetTemplate = $(`<div class="changeset card">
            </div>`);
            let $headerTemplate = $(`<div class="card-header"><button class="btn btn-link" data-toggle="collapse" data-target="#collapse${index}">Version: ${version}</button></div>`);
            let $itemsTemplate = $(`<div id="collapse${index}" class="collapse"><div class="card-body"></div></div>`);
            if(index == 0){
                $itemsTemplate.addClass('show');
            }
            $(changeSet).find('item').each( (index, element)  => {
                let item = $(element).attr('text');
                let $itemTemplate = $(`<li class="item">${item}</li>`);
                $itemsTemplate.find('.card-body').append($itemTemplate);
            });
            $changeSetTemplate.append($headerTemplate);
            $changeSetTemplate.append($itemsTemplate);
            $('#changelog').append($changeSetTemplate);
        });   
        
    });

    $('#showAllChangeSetsBtn').click(() => {
        $('.collapse').addClass('show');
    });

    $('#hideAllChangeSetsBtn').click(() => {
        $('.collapse').removeClass('show');
    });
});