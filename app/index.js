var watson 	= require('watson-developer-cloud'),
	fs 		= require('fs'),
	path 	= require('path'),
	join 	= path.join,
	ua		= require('universal-analytics'),
	visitor = ua('UA-20927727-14');

var visual_recognition = watson.visual_recognition({
    api_key	: "09da0acae4dc03a0c0c02b1728f7b2f8e495c424",
    version: 'v3',
    version_date: '2016-05-20'
});

function checkForFile(){
	getFiles().forEach((file) => {
		var path = join(__dirname, '..', 'images/unprocessed', file)
			newPath = join(__dirname, '..', 'images/processed', file)
			params = {
			    images_file: fs.createReadStream(path)
			};
		visual_recognition.detectFaces(params, function(err, result) {
	        if (err) {
	            //console.log('error');
	            //console.log(err);
	        }
	        else {
	            console.log('success');
	            var action = 'UNKNOWN';
	            if(file.substr(0,4) == 'left'){
	            	action = 'Customer Enters Store';
	            }else{
	            	action = 'Customer Leaves Store';
	            }
	            visitor.event(action, getGender(result) + ' (' + getAge(result) + ')' , getAge(result), function (err) {
				  console.log(err);
				})
	        }
	    });

	    fs.rename(path, newPath, () => console.log('Moved filed'));
	});

	setTimeout(checkForFile, 1000);
}

checkForFile();


function getFiles(){
	var unprocessed = '../images/unprocessed';
	return fs.readdirSync(unprocessed);
}
function getGender(result){
	if(!result.images[0].faces.length || !result.images[0].faces[0].gender) return 'UNKNOWN GENDER';
	return result.images[0].faces[0].gender.gender;
}
function getAge(result){
	if(!result.images[0].faces.length || !result.images[0].faces[0].age) return 'UNKNOWN AGE';
	var minAge = result.images[0].faces[0].age.min,
		maxAge = result.images[0].faces[0].age.max;

	return minAge + '-' + maxAge;
}