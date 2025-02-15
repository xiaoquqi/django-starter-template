<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table';

import { Page } from '@vben/common-ui';

import { Button, message } from 'ant-design-vue';

import { useVbenVxeGrid } from '#/adapter/vxe-table';

import { getPostListApi } from '#/api/sample';

interface RowType {
  id: number;
  title: string;
  content: string;
  author: string;
  category: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

const gridOptions: VxeGridProps<RowType> = {
  checkboxConfig: {
    highlight: true,
    labelField: 'name',
  },
  columns: [
    { title: '序号', type: 'seq', width: 50 },
    { field: 'id', title: 'ID' },
    { field: 'title', title: '标题', showOverflow: true },
    { field: 'content', title: '内容', showOverflow: true },
    { field: 'author', title: '作者' },
    { field: 'category', title: '分类' },
    {
      field: 'tags',
      title: '标签',
      formatter: ({ cellValue }) => Array.isArray(cellValue) ? cellValue.join(', ') : cellValue
    },
    { field: 'created_at', title: '创建时间', sortable: true },
    { field: 'updated_at', title: '更新时间', sortable: true },
  ],
  keepSource: true,
  proxyConfig: {
    ajax: {
      query: async ({ page }) => {
        const response = await getPostListApi({
          page: page.currentPage,
          page_size: page.pageSize,
        });
        return response;
      },
    },
    response: {
      result: 'results',
      total: 'count'
    }
  },
  pagerConfig: {
    enabled: true,
    pageSize: 10,
    pageSizes: [10, 20, 50, 100],
  },
  sortConfig: {
    multiple: true,
  },
  toolbarConfig: {
    custom: true,
    export: true,
    // import: true,
    refresh: true,
    zoom: true,
  },
};

const gridEvents: VxeGridListeners<RowType> = {
  cellClick: ({ row }) => {
    message.info(`cell-click: ${row.title}`);
  },
};

const [Grid, gridApi] = useVbenVxeGrid({
  gridOptions,
});

//async function fetchTableData() {
//  try {
//    gridApi.setLoading(true);
//    const { data } = await getPostListApi();
//    gridApi.setData(data);
//  } catch (error) {
//    message.error('获取数据失败');
//  } finally {
//    gridApi.setLoading(false);
//  }
//}
//
//onMounted(() => {
//  fetchTableData();
//});
</script>

<template>
  <Page
    description="Sample表格示例，用于演示调用Django API获取数据后的数据展现。"
    title="Sample表格示例"
  >
    <Grid table-title="Post列表" table-title-help="用于展现所有Post">
    </Grid>
  </Page>
</template>