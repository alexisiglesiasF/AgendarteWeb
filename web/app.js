const formulario = document.querySelector("form");
const mensaje = document.querySelector("#mensaje");

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mensaje.textContent = "Creando usuario...";

    const datos = {
        nombre: formulario.elements.nombre.value,
        apellido: formulario.elements.apellido.value,
        email: formulario.elements.email.value,
    };

    try {
        const respuesta = await fetch("http://localhost:8000/public/usuario", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(datos),
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok || resultado.status !== "success") {
            throw new Error(resultado.message || "No se pudo crear el usuario.");
        }

        mensaje.textContent = `Usuario creado. ID: ${resultado.data.id}`;
        formulario.reset();
    } catch (error) {
        mensaje.textContent = `Error: ${error.message}`;
    }
});
