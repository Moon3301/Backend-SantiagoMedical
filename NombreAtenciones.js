// let array = []
// const removeAccents = (str) => {
//   return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
// } 
// ;[
//   ...document.querySelectorAll(
//     'body > table:nth-child(18) > tbody > tr > td > div.main > div.module-content.history-module-container > div.history-module > div.history.module-sub-content > ul > li'
//   ),
// ].map((d) => {
//   console.log(
//     d
//       .querySelector(
//         'body > table:nth-child(18) > tbody > tr > td > div.main > div.module-content.history-module-container > div.history-module > div.history.module-sub-content > ul > li > div.history-milestone-container > table > tbody > tr:nth-child(2) > td:nth-child(2) > div > div'
//       )
//       .innerText.trim()
//   )
//   let url = d
//     .querySelector(
//       '.history-milestone-container > table > tbody > tr > td:nth-child(1) > .history-title'
//     )
//     .innerText.split('#')
//   let fecha = ''
// //   d
// //     .querySelector(
// //       'div.event-header > table > tbody > tr > td.event-time-title > div.event-small-text.hora-atencion-plandetratamiento'
// //     )
// //     .innerText.trim()
// //     .split(' ')
//   const tag =  d
//   .querySelector(
//     'div.history-milestone-container > table > tbody > tr:nth-child(2) > td:nth-child(2) > div > div'
//   )
//   console.log(tag.innerText.trim())
//   console.log(removeAccents(tag.innerText.trim())==='Diagnostico')
//   let colorTag = removeAccents(tag.innerText.trim())
//   let color = ''
//   if (colorTag === 'Hay saldo'
//   ) {
//     color = 'green'
//   } else if (
//     colorTag === 'No hay saldo'
//   ) {
//     color = 'yellow'
//   } else if (
//     colorTag === 'Diagnostico'
//   ) {
//     color = 'green'    
//   }  else if (
//     colorTag === 'Finalizada'
//   ) {
//     color = 'green'
//   } else {
//     color = 'red'
//   }
//   array.push({
//     nombre: d
//       .querySelector(
//         '.history-milestone-container > table > tbody > tr > td:nth-child(1) > .history-title'
//       )
//       .innerText.trim(),
//     color: color,
//     fecha: fecha[0],
//     hora: fecha[2],
//     url: `https://santiagomedical.new.softwaremedilink.com/tratamientos/ver/${url[1].trim()}`,
//   })
// })
// return array
let array = [];
const removeAccents = (str) => {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
};
[
  ...document.querySelectorAll(
    "body > table:nth-child(20) > tbody > tr > td > div.main > div.module-content.history-module-container > div.history-module > div.history.module-sub-content > ul > li"
  ),
].map((d) => {
  const tag = d.querySelector(
    "div.history-milestone-container > table > tbody > tr:nth-child(2) > td:nth-child(2) > div > div"
  );
  let colorTag = removeAccents(tag.innerText.trim());
  let color = "";
  let urlTag =
    ".history-milestone-container > table > tbody > tr > td:nth-child(1) > .history-title";
  let url = d.querySelector(urlTag).innerText.split("#");
  let nombreTag =
    ".history-milestone-container > table > tbody > tr > td:nth-child(1) > .history-title";
  let fechaTag1 =
    "div.event-header > table > tbody > tr > td.event-time-title > div.event-small-text.hora-atencion-plandetratamiento";
  let fecha = "";

  if (d.querySelector(fechaTag1) == null) {
    fecha = "";
  } else {
    fecha = d.querySelector(fechaTag1).innerText.trim().split(" ");
  }

  if (colorTag === "Hay saldo") {
    color = "green";
  } else if (colorTag === "No hay saldo") {
    color = "yellow";
  } else if (colorTag === "Diagnostico") {
    color = "green";
  } else if (colorTag === "Finalizada") {
    color = "green";
  } else {
    color = "red";
  }
  array.push({
    nombre: d.querySelector(nombreTag).innerText.trim(),
    color: color,
    fecha: fecha[0],
    hora: "",
    url: `https://santiagomedical.new.softwaremedilink.com/tratamientos/ver/${url[1].trim()}`,
  });
});
return array;
