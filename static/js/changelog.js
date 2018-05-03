
$(document).ready(() => {
    $.get('static/changelog.xml', (changelog) => {
        $(changelog).find('changeSet').each((index, changeSet) => {
            let version = $(changeSet).attr('version');
            let $changeSetTemplate = $(`<div class="changeset card">
            </div>`);
            let $headerTemplate = $(`<div class="card-header"><button class="btn btn-link" data-toggle="collapse" data-target="#collapse${index}" aria-controls="collapse${index}">Version: ${version}</button></div>`);
            let $itemsTemplate = $(`<div id="collapse${index}" class="collapse card-body" data-parent="#changelog"</div>`);
            if(index == 0){
                $itemsTemplate.addClass('show');
            }
            $(changeSet).find('item').each( (index, element)  => {
                let item = $(element).attr('text');
                let $itemTemplate = $(`<li class="item">${item}</li>`);
                $itemsTemplate.append($itemTemplate)
            });
            $changeSetTemplate.append($headerTemplate);
            $changeSetTemplate.append($itemsTemplate);
            $('#changelog').append($changeSetTemplate);
        });   
        $('#showAllChangeSetsBtn').click(() => {
            $('.collapse').collapse('show');
        });

        $('#hideAllChangeSetsBtn').click(() => {
            $('.collapse').collapse('hide');
        });
    });
});