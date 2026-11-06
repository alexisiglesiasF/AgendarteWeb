const formulario = document.querySelector(".formulario-evento");
const mensaje = document.querySelector("#mensaje");
const apiUrl = "http://localhost:8000";

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mensaje.textContent = "Buscando usuario...";

    const idUsuario = formulario.elements.id_usuario.value;

    try {
        const respuestaUsuario = await fetch(
            `${apiUrl}/public/usuario/${idUsuario}`
        );
        const resultadoUsuario = await respuestaUsuario.json();

        if (!respuestaUsuario.ok || resultadoUsuario.status !== "success") {
            throw new Error(
                resultadoUsuario.message || "No se encontró el usuario."
            );
        }

        const usuarioId = resultadoUsuario.data.id;
        const fechaHora = `${formulario.elements.fecha.value}T${formulario.elements.hora.value}:00`;
        const proyectoElegido = formulario.elements.id_proyecto.value;

        const datosEvento = {
            usuario_id: usuarioId,
            id_proyecto: proyectoElegido ? Number(proyectoElegido) : null,
            nombre: formulario.elements.nombre.value,
            ubicacion: formulario.elements.ubicacion.value || null,
            tipo: formulario.elements.tipo.value,
            fecha: fechaHora,
            hora: formulario.elements.hora.value,
            estado: formulario.elements.estado.value,
            notas: formulario.elements.notas.value || null,
        };

        mensaje.textContent = "Creando evento...";

        const respuestaEvento = await fetch(`${apiUrl}/public/evento`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(datosEvento),
        });
        const resultadoEvento = await respuestaEvento.json();

        if (!respuestaEvento.ok || resultadoEvento.status !== "success") {
            throw new Error(
                resultadoEvento.message || "No se pudo crear el evento."
            );
        }

        mensaje.textContent = `Evento creado. ID: ${resultadoEvento.data.id}`;
        const respuestaEventos = await fetch(
    `${apiUrl}/public/evento?usuario_id=${usuarioId}`
);
const resultadoEventos = await respuestaEventos.json();

if (!respuestaEventos.ok || resultadoEventos.status !== "success") {
    throw new Error("No se pudieron cargar los eventos.");
}

const lista = document.querySelector("#lista-eventos");
lista.replaceChildren();

for (const evento of resultadoEventos.data) {
    const elemento = document.createElement("li");
    elemento.textContent = `${evento.nombre} — ${evento.tipo}`;
    lista.appendChild(elemento);
}
    } catch (error) {
        mensaje.textContent = `Error: ${error.message}`;
    }
});


