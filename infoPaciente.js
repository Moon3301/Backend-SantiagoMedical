const nombrePaciente = document.querySelector('#nombre').getValue()
const apellidosPaciente = document.querySelector('#apellidos').getValue()
const rutPaciente = document.querySelector('#rut').getValue()
const mailPaciente = document.querySelector('#mail').getValue()
const celularPaciente = document.querySelector('#celular').getValue()
const medicoPaciente =  document.querySelector('#personales_main > div:nth-child(21) > div > div').innerText == "No hay registro." 
                        ? '' 
                        : document.querySelector('#personales_main > div:nth-child(21) > div > div > div > div').textContent

return [
  nombrePaciente,
  apellidosPaciente,
  rutPaciente,
  mailPaciente,
  celularPaciente,
  medicoPaciente,
]
