import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'ic:baseline-view-in-ar',
      keepAlive: true,
      order: 1000,
      title: $t('sample.title'),
    },
    name: 'Sample',
    path: '/sample',
    children: [
      {
        meta: {
          title: $t('sample.post'),
        },
        name: 'Post',
        path: '/sample/post',
        component: () => import('#/views/sample/index.vue'),
      },
    ],
  },
];

export default routes;
