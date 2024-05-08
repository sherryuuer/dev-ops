[Document](https://cloud.google.com/dataform/docs/reference/sample-scripts?hl=ja)


## 共通変数はjavascriptファイルで設定する:project_name 

includes/constants.js 
```js
const project_id = "project_id"; 
 
module.exports = { 
project_id 
}; 
```

## Create or Replace datamart 

```js
config {  
    type: "table", 
    schema: "dataset_name", 
    tags: ["ds_", "sche_"], 
} 
 
SELECT  
    user_name,  
    user_id,
FROM  
    ${ref("source_table")} 
```

※dsはデータセット、scheはスケジュール 

## Delete & Insert

```js
config { 
    type: "operations", 
    schema: "dataset_name", 
    HasOutput: true, 
    tags: ["ds_", "sche_"],
} 


DELETE FROM ${self()}
INSERT INTO ${self()}
SELECT 
    *
FROM 
    ${ref("source_table")}  
```

## テーブルを宣言するだけ（依存関係を示すため）

```js
config { 
    type: "declaration", 
    database: "project_name", 
    schema: "dataset_name", 
    Name: "tablename" 
}
```

## 他のフォーマット

### VIEW

※本件ではDFでview作らない（定期更新でないため）
```js
config { 
    type: "view" 
}

SELECT 
    *
FROM
    ${ref("source_table")}   
```
 
※マテビューも固定のものはDFで作らない、定期バッチになるものは相談することでDFで作成するかどうかを決める
```js
config { 
    type: "view", 
    materialized: true,
} 
 
SELECT 
    *
FROM
    ${ref("source_table")}
```

### 増分更新
```js
config { 
    type: "incremental", 
    uniqueKey: ["transaction_id"],
}

SELECT 
    timestamp,
    action,
FROM 
    ${ref("source_table")}
${ when(incremental(), `WHERE timestamp > (SELECT MAX(timestamp) FROM ${self()})`) }
```

[増分更新](https://cloud.google.com/dataform/docs/incremental-tables?hl=ja)

