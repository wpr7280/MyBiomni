import { defineConfig, presetAttributify, presetUno } from 'unocss'

export default defineConfig({
  exclude: [
    'node_modules',
    '.git',
    '.github',
    '.husky',
    '.vscode',
    'build',
    'dist',
    'mock',
    'public',
    './stats.html',
  ],
  presets: [presetUno(), presetAttributify()],
  shortcuts: [
    ['wh-full', 'w-full h-full'],
    ['f-c-c', 'flex justify-center items-center'],
    ['flex-col', 'flex flex-col'],
    ['absolute-lt', 'absolute left-0 top-0'],
    ['absolute-lb', 'absolute left-0 bottom-0'],
    ['absolute-rt', 'absolute right-0 top-0'],
    ['absolute-rb', 'absolute right-0 bottom-0'],
    ['absolute-center', 'absolute-lt f-c-c wh-full'],
    ['text-ellipsis', 'truncate'],
  ],
  rules: [
    [/^bc-(.+)$/, ([, color]) => ({ 'border-color': `#${color}` })],
    [
      'card-shadow',
      { 'box-shadow': '0 1px 2px -2px #00000029, 0 3px 6px #0000001f, 0 5px 12px 4px #00000017' },
    ],
  ],
  theme: {
    colors: {
      // 主色调系统
      primary: {
        50: '#E6F4FF',
        100: '#BAE7FF',
        200: '#91D5FF',
        300: '#69C0FF',
        400: '#40A9FF',
        500: '#1C9CEB', // 主色
        600: '#0F7BC7',
        700: '#0050B3',
        800: '#003A8C',
        900: '#002766',
      },
      
      // 辅助色系统
      success: {
        50: '#F6FFED',
        100: '#D9F7BE',
        200: '#B7EB8F',
        300: '#95DE64',
        400: '#73D13D',
        500: '#52C41A',
        600: '#389E0D',
        700: '#237804',
        800: '#135200',
        900: '#092B00',
      },
      
      warning: {
        50: '#FFFBE6',
        100: '#FFF1B8',
        200: '#FFE58F',
        300: '#FFD666',
        400: '#FFC53D',
        500: '#FAAD14',
        600: '#D48806',
        700: '#AD6800',
        800: '#874D00',
        900: '#613400',
      },
      
      error: {
        50: '#FFF2F0',
        100: '#FFCCC7',
        200: '#FFA39E',
        300: '#FF7875',
        400: '#FF4D4F',
        500: '#F5222D',
        600: '#D9363E',
        700: '#A8071A',
        800: '#820014',
        900: '#5C0011',
      },
      
      info: {
        50: '#E6F7FF',
        100: '#BAE7FF',
        200: '#91D5FF',
        300: '#69C0FF',
        400: '#40A9FF',
        500: '#1890FF',
        600: '#096DD9',
        700: '#0050B3',
        800: '#003A8C',
        900: '#002766',
      },
      
      // 中性色系统
      gray: {
        50: '#FAFAFA',
        100: '#F5F5F5',
        200: '#F0F0F0',
        300: '#D9D9D9',
        400: '#BFBFBF',
        500: '#8C8C8C',
        600: '#595959',
        700: '#434343',
        800: '#262626',
        900: '#1F1F1F',
      },
    },
    
    // 扩展阴影系统
    boxShadow: {
      'primary-1': '0 1px 2px 0 rgba(28, 156, 235, 0.05)',
      'primary-2': '0 2px 4px 0 rgba(28, 156, 235, 0.1)',
      'primary-3': '0 4px 8px 0 rgba(28, 156, 235, 0.15)',
      'primary-4': '0 8px 16px 0 rgba(28, 156, 235, 0.2)',
    },
  },
})
