if(document.querySelector('body > table:nth-child(21) > tbody > tr > td > div.main > div.module-content.history-module-container > div.history-module > div.history.module-sub-content > ul > li:nth-child(1) > div.event-header > table > tbody > tr > td.event-time-title > div.event-small-title.titulo-fecha-atencion-plandetratamiento') !== null){
    return document.querySelector('body > table:nth-child(21) > tbody > tr > td > div.main > div.module-content.history-module-container > div.history-module > div.history.module-sub-content > ul > li:nth-child(1) > div.event-header > table > tbody > tr > td.event-time-title > div.event-small-title.titulo-fecha-atencion-plandetratamiento').innerText
}else{
    return 'NADA'
}