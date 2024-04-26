let array = [];
[...document.querySelectorAll("#display_consulta > div > table.table.treatment-plan > tbody > tr.vmiddle")].map((d) => {
    array.push({
        nombre: d.querySelectorAll("tr > td:nth-child(2) > div > div")[0].innerText.replace("Más Información", "").replace(" -  Eliminar", "").trim(),
        codigo: d.querySelectorAll("tr > td:nth-child(2) > div > div:nth-child(3)")[0].id.replace("info_", ""),
        descuento: d.querySelectorAll("tr > td:nth-child(3)")[0].innerText.replace("%", "").trim(),
        precio: d.querySelectorAll("tr > td:nth-child(4)")[0].innerText.replace("$", "").replace(".", "").replace(".", "").trim(),
    });
});
return array;