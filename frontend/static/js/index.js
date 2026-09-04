document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("btn-diarias").addEventListener("click", () => cargarDiarias());
    document.getElementById("btn-compras").addEventListener("click", () => cargarCompras());
    document.getElementById("btn-anual").addEventListener("click", () => cargarAnual());
    document.getElementById("btn-productos").addEventListener("click", () => cargarProductos(true));
    document.getElementById("btn-precios").addEventListener("click", () => mostrarPrecios());
    document.getElementById("btn-aplicar-filtro").addEventListener("click", aplicarFiltro);
    document.getElementById("btn-limpiar-filtro").addEventListener("click", limpiarFiltro);
    
    document.getElementById("btn-consultar-precio").addEventListener("click", consultarPrecio);
    document.getElementById("input-producto").addEventListener("keyup", (e) => {
        if (e.key === "Enter") consultarPrecio();
    });

    cargarAnual();
});

let graficoActual = "anual";
let productosOffset = 0;
const productosLimite = 40;
let listaProductosCache = null;

function obtenerFechas() {
    const inicio = document.getElementById("fecha-inicio").value;
    const fin = document.getElementById("fecha-fin").value;
    return { inicio, fin };
}

function construirUrl(baseUrl) {
    const { inicio, fin } = obtenerFechas();
    const params = new URLSearchParams();
    if (inicio) params.append("fecha_inicio", inicio);
    if (fin) params.append("fecha_fin", fin);
    const query = params.toString();
    if (!query) return baseUrl;
    const separator = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${separator}${query}`;
}

function limpiarContenedor() {
    const graficoDiv = document.getElementById("grafico");
    if (graficoDiv) {
        if (typeof Plotly !== 'undefined') {
            Plotly.purge(graficoDiv);
        }
        graficoDiv.style.cssText = '';
        graficoDiv.innerHTML = '';
        graficoDiv.className = '';
        graficoDiv.style.width = '100%';
        graficoDiv.style.display = 'block';
    }
}

function resetearContenedorGrafico() {
    const graficoDiv = document.getElementById("grafico");
    const container = document.getElementById("grafico-container");
    
    if (graficoDiv) {
        if (typeof Plotly !== 'undefined') {
            Plotly.purge(graficoDiv);
        }
        graficoDiv.style.cssText = '';
        graficoDiv.innerHTML = '';
        graficoDiv.className = '';
        graficoDiv.style.width = '100%';
        graficoDiv.style.display = 'block';
        graficoDiv.style.height = '';
        graficoDiv.style.minHeight = '';
        graficoDiv.style.overflow = '';
        graficoDiv.style.flex = '';
    }
    
    if (container) {
        container.style.minHeight = '';
        container.style.height = '';
        container.style.overflow = '';
    }
    
    void document.getElementById("grafico").offsetHeight;
}

function ocultarElementosSecundarios() {
    document.getElementById("controles-precios").style.display = "none";
    eliminarBotonesPaginacion();
    resetearContenedorGrafico();
}

function mostrarMensaje(mensaje) {
    resetearContenedorGrafico();
    const graficoDiv = document.getElementById("grafico");
    if (graficoDiv) {
        graficoDiv.innerHTML = `
            <div class="mensaje-grafico">
                ${mensaje}
            </div>
        `;
    }
}

function aplicarFiltro() {
    if (graficoActual === "anual") cargarAnual();
    else if (graficoActual === "mensual") cargarCompras();
    else if (graficoActual === "diarias") cargarDiarias();
    else if (graficoActual === "productos") cargarProductos(true);
    else if (graficoActual === "precios") {
        const producto = document.getElementById("input-producto").value.trim();
        if (producto) consultarPrecio();
        else mostrarMensaje("Seleccione un producto para aplicar el filtro de fechas");
    }
}

function limpiarFiltro() {
    document.getElementById("fecha-inicio").value = "";
    document.getElementById("fecha-fin").value = "";
    aplicarFiltro();
}

async function cargarAnual() {
    graficoActual = "anual";
    ocultarElementosSecundarios();
    resetearContenedorGrafico();
    try {
        const url = construirUrl("/api/dashboard/anual");
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const datos = await response.json();
        if (!datos || datos.length === 0) {
            mostrarMensaje("No hay datos para el periodo seleccionado");
            return;
        }
        renderizarGrafico(datos, "anual");
    } catch (err) {
        mostrarMensaje(`Error: ${err.message}`);
    }
}

async function cargarCompras() {
    graficoActual = "mensual";
    ocultarElementosSecundarios();
    resetearContenedorGrafico();
    try {
        const url = construirUrl("/api/dashboard/compras");
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const datos = await response.json();
        if (!datos || datos.length === 0) {
            mostrarMensaje("No hay datos para el periodo seleccionado");
            return;
        }
        renderizarGrafico(datos, "mensual");
    } catch (err) {
        mostrarMensaje(`Error: ${err.message}`);
    }
}

async function cargarDiarias() {
    graficoActual = "diarias";
    ocultarElementosSecundarios();
    resetearContenedorGrafico();
    try {
        const url = construirUrl("/api/dashboard/compras-diarias");
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const datos = await response.json();
        if (!datos || datos.length === 0) {
            mostrarMensaje("No hay datos para el periodo seleccionado");
            return;
        }
        renderizarGrafico(datos, "diarias");
    } catch (err) {
        mostrarMensaje(`Error: ${err.message}`);
    }
}

async function cargarProductos(reset = true) {
    graficoActual = "productos";
    ocultarElementosSecundarios();
    resetearContenedorGrafico();
    try {
        if (reset) {
            productosOffset = 0;
            eliminarBotonesPaginacion();
        }
        const url = construirUrl(`/api/dashboard/compras-productos?limite=${productosLimite}&offset=${productosOffset}`);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const datos = await response.json();
        if (!datos || datos.length === 0) {
            mostrarMensaje("No hay datos para el periodo seleccionado");
            return;
        }
        renderizarGraficoProductos(datos);
        const hayMas = datos.length === productosLimite;
        const hayMenos = productosOffset > 0;
        crearBotonesPaginacion(hayMenos, hayMas);
    } catch (err) {
        mostrarMensaje(`Error: ${err.message}`);
    }
}

function renderizarGraficoProductos(datos) {
    const graficoDiv = document.getElementById("grafico");
    if (!graficoDiv) return;
    
    resetearContenedorGrafico();

    if (!datos || datos.length === 0) {
        mostrarMensaje("No hay productos para mostrar");
        eliminarBotonesPaginacion();
        return;
    }

    const productos = datos.map(d => d.producto);
    const totalUnidades = datos.map(d => d.total_vendido);
    const totalGastado = datos.map(d => d.total_recaudado);

    const trace = {
        x: productos,
        y: totalUnidades,
        type: "bar",
        marker: { color: "#8E44AD" },
        hovertemplate: "<b>%{x}</b><br>Unidades compradas: %{y}<br>Total compras: $%{customdata:,.0f}<extra></extra>",
        customdata: totalGastado
    };

    const layout = {
        template: "plotly_white",
        margin: { l: 80, r: 20, t: 40, b: 120 },
        title: { text: "Top productos mas comprados", x: 0.5, font: { size: 16 } },
        xaxis: { 
            title: { text: "Producto", font: { size: 11 } }, 
            tickangle: -45, 
            tickfont: { size: 8 } 
        },
        yaxis: { 
            title: { text: "Unidades compradas", font: { size: 11 } }, 
            tickformat: ",d", 
            gridcolor: "#eee", 
            zeroline: false 
        },
        bargap: 0.2,
        autosize: true,
        responsive: true,
        height: 400
    };

    Plotly.react("grafico", [trace], layout, { responsive: true });
}

function crearBotonesPaginacion(hayMenos, hayMas) {
    eliminarBotonesPaginacion();
    if (!hayMenos && !hayMas) return;

    const container = document.getElementById("grafico-container");
    const divBotones = document.createElement("div");
    divBotones.id = "paginacion-productos";
    divBotones.className = "paginacion-botones";

    if (hayMenos) {
        const btn = document.createElement("button");
        btn.textContent = "← Anterior";
        btn.className = "btn-paginacion";
        btn.addEventListener("click", () => {
            if (productosOffset - productosLimite >= 0) {
                productosOffset -= productosLimite;
                cargarProductos(false);
            }
        });
        divBotones.appendChild(btn);
    }

    if (hayMas) {
        const btn = document.createElement("button");
        btn.textContent = "Siguiente →";
        btn.className = "btn-paginacion";
        btn.addEventListener("click", () => {
            productosOffset += productosLimite;
            cargarProductos(false);
        });
        divBotones.appendChild(btn);
    }

    container.appendChild(divBotones);
}

function eliminarBotonesPaginacion() {
    const div = document.getElementById("paginacion-productos");
    if (div) div.remove();
}

async function mostrarPrecios() {
    graficoActual = "precios";
    ocultarElementosSecundarios();
    resetearContenedorGrafico();
    document.getElementById("controles-precios").style.display = "block";
    await cargarListaProductos();
    mostrarMensaje("Seleccione un producto y presione 'Consultar'");
}

async function cargarListaProductos() {
    if (listaProductosCache) {
        actualizarDatalist(listaProductosCache);
        return;
    }
    try {
        const response = await fetch("/api/dashboard/productos-lista");
        if (!response.ok) throw new Error("Error al cargar productos");
        const productos = await response.json();
        listaProductosCache = productos;
        actualizarDatalist(productos);
    } catch (err) {
        const datalist = document.getElementById("lista-productos");
        datalist.innerHTML = `<option value="Error al cargar productos">`;
    }
}

function actualizarDatalist(productos) {
    const datalist = document.getElementById("lista-productos");
    datalist.innerHTML = productos.map(p => `<option value="${p}">`).join("");
}

async function consultarPrecio() {
    const input = document.getElementById("input-producto");
    const producto = input.value.trim();
    if (!producto) {
        mostrarMensaje("Por favor, ingrese un producto.");
        return;
    }

    try {
        const url = construirUrl(`/api/dashboard/precios-producto?producto=${encodeURIComponent(producto)}`);
        const response = await fetch(url);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        const datos = await response.json();
        if (!datos || datos.length === 0) {
            mostrarMensaje(`No hay datos de precios para "${producto}" en el periodo seleccionado.`);
            return;
        }
        renderizarTablaPrecios(datos);
    } catch (err) {
        mostrarMensaje(`Error: ${err.message}`);
    }
}

function renderizarTablaPrecios(datos) {
    const graficoDiv = document.getElementById("grafico");
    if (!graficoDiv) return;

    resetearContenedorGrafico();

    graficoDiv.style.height = 'auto';
    graficoDiv.style.overflow = 'visible';
    graficoDiv.style.display = 'block';
    graficoDiv.style.width = '100%';
    graficoDiv.style.minHeight = '200px';
    graficoDiv.style.flex = 'none';
    graficoDiv.className = 'tabla-precios-contenedor';

    const producto = document.getElementById("input-producto").value;

    let html = `
        <div class="tabla-precios" style="padding: 10px;">
            <h3 style="text-align: center; margin-bottom: 15px; color: #2c3e50;">
                Evolucion de precios para: <strong>${producto}</strong>
            </h3>
            <div style="max-height: 500px; overflow-y: auto; border-radius: 8px; border: 1px solid #ddd;">
                <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <thead>
                        <tr style="background-color: #8E44AD; color: white; position: sticky; top: 0; z-index: 10;">
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Fecha</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Precio unitario ($)</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    datos.forEach((item, index) => {
        const colorFila = index % 2 === 0 ? '#f9f9f9' : '#ffffff';
        html += `
            <tr style="background-color: ${colorFila};">
                <td style="padding: 10px; border: 1px solid #ddd;">${item.fecha}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: 500;">
                    $${item.precio.toFixed(2)}
                </td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>
            <p style="text-align: center; margin-top: 15px; color: #7f8c8d; font-size: 13px;">
                Mostrando ${datos.length} registros (solo cambios de precio > $10)
            </p>
        </div>
    `;

    graficoDiv.innerHTML = html;
}

function renderizarGrafico(datos, tipo) {
    const graficoDiv = document.getElementById("grafico");
    if (!graficoDiv) return;
    
    resetearContenedorGrafico();

    let trace = {};
    const layout = {
        template: "plotly_white",
        margin: { l: 100, r: 20, t: 40, b: 50 },
        yaxis: { tickformat: "$~s", gridcolor: "#eee", zeroline: false },
        autosize: true,
        responsive: true,
        height: 400
    };

    if (tipo === "anual") {
        trace = {
            x: datos.map(d => d.anio),
            y: datos.map(d => d.compras),
            type: "bar",
            marker: { color: "#27ae60" },
            hovertemplate: "<b>%{x}</b><br>Compras: $%{y:,.0f}<extra></extra>"
        };
        layout.title = { text: "Compras por año", x: 0.5, font: { size: 16 } };
        layout.xaxis = { title: { text: "Año", font: { size: 12 } } };
        layout.yaxis.title = { text: "Compras", font: { size: 12 } };
    } else if (tipo === "mensual") {
        trace = {
            x: datos.map(d => d.periodo),
            y: datos.map(d => d.compras),
            type: "bar",
            marker: { color: "#2E86DE" },
            hovertemplate: "<b>%{x}</b><br>Compras: $%{y:,.0f}<extra></extra>"
        };
        layout.title = { text: "Compras mensuales", x: 0.5, font: { size: 16 } };
        layout.xaxis = { title: { text: "Mes", font: { size: 12 } }, tickangle: -45 };
        layout.yaxis.title = { text: "Compras", font: { size: 12 } };
        layout.margin.b = 70;
    } else if (tipo === "diarias") {
        trace = {
            x: datos.map(d => d.dia),
            y: datos.map(d => d.compras),
            type: "bar",
            marker: { color: "#E67E22" },
            hovertemplate: "<b>%{x}</b><br>Compras: $%{y:,.0f}<extra></extra>"
        };
        layout.title = { text: "Compras diarias", x: 0.5, font: { size: 16 } };
        layout.xaxis = { title: { text: "Fecha", font: { size: 12 } }, tickangle: -45 };
        layout.yaxis.title = { text: "Compras", font: { size: 12 } };
        layout.margin.b = 80;
    }

    Plotly.react("grafico", [trace], layout, { responsive: true });
}