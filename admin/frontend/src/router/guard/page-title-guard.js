const baseTitle = import.meta.env.VITE_TITLE

export function createPageTitleGuard(router) {
  router.afterEach(async (to) => {
    const pageTitle = to.meta?.title
    if (pageTitle) {
      let translated = pageTitle
      // Translate i18n keys like "menu.user_management"
      if (pageTitle.startsWith('menu.')) {
        try {
          const i18n = (await import('~/i18n')).default
          translated = i18n.global.t(pageTitle)
        } catch {
          translated = pageTitle.split('.').pop().replace(/_/g, ' ')
        }
      }
      document.title = `${translated} | ${baseTitle}`
    } else {
      document.title = baseTitle
    }
  })
}
