import { defineOverridesPreferences } from '@vben/preferences';

/**
 * @description 项目配置文件
 * 只需要覆盖项目中的一部分配置，不需要的配置不用覆盖，会自动使用默认配置
 * !!! 更改配置后请清空缓存，否则可能不生效
 */
export const overridesPreferences = defineOverridesPreferences({
  // overrides
  app: {
    name: import.meta.env.VITE_APP_TITLE,
    dynamicTitle: false,
    enablePreferences: false
  },
  breadcrumb: {
    hideOnlyOne: true,
    showHome: true,
    styleType: "background"
  },
  copyright: {
    companyName: "Mito",
    companySiteLink: "https://github.com/xiaoquqi",
    date: "2025"
  },
  footer: {
    enable: true
  },
  shortcutKeys: {
    enable: false
  },
  tabbar: {
    enable: false,
    styleType: "brisk"
  },
  theme: {
    mode: "light",
    semiDarkSidebar: true
  },
  transition: {
    name: "fade-down"
  },
  widget: {
    fullscreen: false,
    globalSearch: false,
    lockScreen: false,
    themeToggle: false
  }
});