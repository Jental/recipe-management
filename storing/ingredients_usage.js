// ingredient popularity
print("id,name,count");
db.recipes
    .aggregate([
        {$unwind: "$ingredients"},
        {$group: {
            _id: "$ingredients.id",
            name: {$first: "$ingredients.name"},
            count: {$sum: 1}}},
        {$sort: {count: -1}}])
    .forEach(function(row){
        print("" + row._id.valueOf() + "," + row.name + "," + row.count);
    });
