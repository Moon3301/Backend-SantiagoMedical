let array = []
;[
  ...document.querySelectorAll(
    '#display_consulta > div > table.table.treatment-plan > tbody > tr.vmiddle'
  ),
].map((d) => {
  let nombreTag = d
  .querySelectorAll('tr > td:nth-child(2) > div > div')[0]
  .innerText.split('\n')
  array.push({
    nombre: nombreTag[0],
    codigo: d
      .querySelectorAll('tr > td:nth-child(2) > div > div:nth-child(3)')[0]
      .id.replace('info_', '')
      .replace('- Desasociar Pago', ''),
    descuento: d
      .querySelectorAll('tr > td:nth-child(3)')[0]
      .innerText.replace('%', '')
      .replace('- Desasociar Pago', '')
      .trim(),
    precio: d
      .querySelectorAll('tr > td:nth-child(4)')[0]
      .innerText.replace('$', '')
      .replace('.', '')
      .trim(),
    color: d.querySelector('#display_consulta > div > table.table.treatment-plan > tbody > tr > td:nth-child(5) > i').attributes[1].value.replace('!important;margin-right:10px;','').replace('color:','').trim()
  })
})
console.log(array)
return array
