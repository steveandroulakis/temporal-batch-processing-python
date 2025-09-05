/*
 *  Copyright (c) 2020 Temporal Technologies, Inc. All Rights Reserved
 *
 *  Copyright 2012-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 *  Modifications copyright (C) 2017 Uber Technologies, Inc.
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"). You may not
 *  use this file except in compliance with the License. A copy of the License is
 *  located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 *  or in the "license" file accompanying this file. This file is distributed on
 *  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 *  express or implied. See the License for the specific language governing
 *  permissions and limitations under the License.
 */

package io.temporal.samples.batchprocessing;

import io.temporal.samples.batchprocessing.web.ServerInfo;
import io.temporal.worker.WorkerFactory;
import io.temporal.worker.WorkerOptions;

public class Worker {

  @SuppressWarnings("CatchAndPrintStackTrace")
  public static void main(String[] args) throws Exception {
    int metricsPort = args.length > 0 ? Integer.parseInt(args[0]) : 8085;

    final String TASK_QUEUE = ServerInfo.getTaskqueue();

    // set activities per second across *all* workers
    // prevents resource exhausted errors
    WorkerOptions options =
        WorkerOptions.newBuilder().setMaxTaskQueueActivitiesPerSecond(150).build();

    // worker factory that can be used to create workers for specific task queues
    WorkerFactory factory = WorkerFactory.newInstance(TemporalClient.get(metricsPort));
    io.temporal.worker.Worker workerForCommonTaskQueue = factory.newWorker(TASK_QUEUE, options);
    workerForCommonTaskQueue.registerWorkflowImplementationTypes(
        BatchParentWorkflowImpl.class, BatchChildWorkflowImpl.class);
    BatchActivities batchActivities = new BatchActivitiesImpl();
    workerForCommonTaskQueue.registerActivitiesImplementations(batchActivities);

    // Start all workers created by this factory.
    factory.start();
    System.out.println("Worker started for task queue: " + "BatchParentWorkflowTaskQueue");
    System.out.println("Metrics available at: http://localhost:" + metricsPort + "/metrics");
  }
}
