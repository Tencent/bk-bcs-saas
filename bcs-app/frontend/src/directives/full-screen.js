export default {
    inserted (el, bind) {
        const parentNode = el.parentNode
        if (!parentNode) return

        const icon = document.createElement('i')
        icon.className = 'bcs-icon bcs-icon-full-screen'
        icon.style.cssText = 'position: absolute;right: 20px;top: 15px;cursor: pointer;z-index: 200'
        icon.addEventListener('click', () => {
            if (icon.className === 'bcs-icon bcs-icon-full-screen') {
                icon.className = 'bcs-icon bcs-icon-un-full-screen'
                icon.style.position = 'fixed'
                el.classList.add('bcs-full-screen')
            } else {
                icon.className = 'bcs-icon bcs-icon-full-screen'
                icon.style.position = 'absolute'
                el.classList.remove('bcs-full-screen')
            }
        })

        parentNode.append(icon)
    }
}
