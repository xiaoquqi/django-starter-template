<script lang="ts" setup>
import type { VxeGridListeners, VxeGridProps } from '#/adapter/vxe-table';

import { Page } from '@vben/common-ui';

import { Button, message } from 'ant-design-vue';

import { useVbenVxeGrid } from '#/adapter/vxe-table';

//import DocButton from '../doc-button.vue';
//import { MOCK_TABLE_DATA } from './table-data';

import { getPostListApi } from '#/api/sample';
import { onMounted } from 'vue';

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
  columns: [
    { title: '序号', type: 'seq', width: 50 },
    { field: 'id', title: 'ID' },
    { field: 'title', title: '标题', showOverflow: true },
    { field: 'content', title: '内容', showOverflow: true },
    { field: 'author', title: '作者' },
    { field: 'category', title: '分类' },
    { field: 'tags', title: '标签' },
    { field: 'created_at', title: '创建时间', sortable: true },
    { field: 'updated_at', title: '更新时间', sortable: true },
  ],
  data: [],
  pagerConfig: {
    enabled: true,
    pageSize: 10,
    pageSizes: [10, 20, 50, 100],
  },
  sortConfig: {
    multiple: true,
  },
};

const gridEvents: VxeGridListeners<RowType> = {
  cellClick: ({ row }) => {
    message.info(`cell-click: ${row.title}`);
  },
};

const [Grid, gridApi] = useVbenVxeGrid({ gridEvents, gridOptions });

const showBorder = gridApi.useStore((state) => state.gridOptions?.border);
const showStripe = gridApi.useStore((state) => state.gridOptions?.stripe);

function changeBorder() {
  gridApi.setGridOptions({
    border: !showBorder.value,
  });
}

function changeStripe() {
  gridApi.setGridOptions({
    stripe: !showStripe.value,
  });
}

function changeLoading() {
  gridApi.setLoading(true);
  setTimeout(() => {
    gridApi.setLoading(false);
  }, 2000);
}

async function fetchTableData() {
  try {
    gridApi.setLoading(true);
    const { data } = await getPostListApi();
    gridApi.setData(data);
  } catch (error) {
    message.error('获取数据失败');
  } finally {
    gridApi.setLoading(false);
  }
}

onMounted(() => {
  fetchTableData();
});
</script>

<template>
  <Page
    description="Sample表格示例，使用vxe-table组件，并进行二次封装。"
    title="Sample表格示例"
  >
    <Grid table-title="Post列表" table-title-help="用于展现所有Post">
    </Grid>
  </Page>
</template>