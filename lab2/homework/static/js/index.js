
async function submit () {
    const batch = [];
    for (const input of document.getElementsByClassName("ip-input")) {
        if (input.value.length !== 0)
            batch.push(input.value);
    }
    const resp = await fetch("/api/batch", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        body: JSON.stringify(batch)
    });

    const data = await resp.json();
    console.log(resp.status)
    if (resp.status >= 400) {
        const errors = "".concat(...data.map(elem => `${elem.query}: ${elem.message}\n`))
        alert(`ERROR:\n${errors}`);
        return;
    }
    window.location.href = `/result/${data.id}`
}

async function getRawJSON() {
    const path = window.location.pathname.split("/");
    console.log(path)
    const id = path[path.length - 1];
    if (id === undefined)
        return
    window.location.href = `/result/json/${id}`;
}